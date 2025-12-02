from odoo import models, fields, api
from odoo.exceptions import ValidationError
import os



class ReceivingWood(models.Model):
    _name = 'receiving.wood'
    _description = 'Receiving Wood'

    partner_id = fields.Many2one(
        'res.partner',
        'Отримати з',
        required=True,
        domain="[('category_id.name', '=', 'Постачальник')]"
    )
    invoice_number = fields.Integer('Номер накладної', required=True)

    move_ids_without_package = fields.One2many(
        'receiving.wood.line', 'receiving_wood_id', string="Stock move")

    product_quantity_t = fields.Float(compute='_compute_total_move_quantity', store=True, digits=(16, 3))

    document_ids = fields.Many2many('ir.attachment', string='Завантажити документи')
    currency_id = fields.Many2one('res.currency', string="Валюта", required=True,)

    total_price = fields.Monetary('Ціна', currency_field='currency_id', compute='_compute_total_price')

    @api.depends('move_ids_without_package.price')
    def _compute_total_price(self):
        for obj in self:
            obj.total_price = sum(obj.move_ids_without_package.mapped('price'))

    @api.depends('move_ids_without_package.quantity')
    def _compute_total_move_quantity(self):
        for picking in self:
            picking.product_quantity_t = sum(picking.move_ids_without_package.mapped('quantity'))

    @api.constrains('document_ids')
    def _check_file_type(self):
        for record in self:
            for attachment in record.document_ids:
                # Отримуємо розширення файлу
                file_ext = os.path.splitext(attachment.name)[1].lower()
                # Визначаємо дозволені розширення
                allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', 'svg', '.jpg', '.jpeg', '.png']

                if file_ext not in allowed_extensions:
                    raise ValidationError(
                        f'Файл "{attachment.name}" має недопустиме розширення. '
                        f'Дозволені формати: {", ".join(allowed_extensions)}'
                    )

                # Перевірка розміру файлу (25MB в байтах)
                max_size = 25 * 1024 * 1024  # 25MB
                if attachment.file_size > max_size:
                    raise ValidationError(
                        f'Файл "{attachment.name}" завеликий. '
                        f'Максимальний розмір файлу: 25MB'
                    )

    @api.model
    def default_get(self, fields_list):
        res = super(ReceivingWood, self).default_get(fields_list)
        products = self.env['product.product'].search([('name', 'in', ['Бук сорт A', 'Бук сорт B', 'Бук сорт C', 'Бук сорт D'])])
        move_lines = []
        for product in products:
            move_lines.append((0, 0, {'product_id': product.id, 'quantity': 0.0}))
        res['move_ids_without_package'] = move_lines
        return res

    def action_create_operations(self):
        stock_picking_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']

        for record in self:

            valid_moves = record.move_ids_without_package.filtered(lambda line: line.quantity > 0)

            if not valid_moves:
                raise ValidationError("Не знайдено продуктів з кількістю більше 0.")

            picking_type = self.env['stock.picking.type'].search([('name', '=', 'Надходження')],
                                                                 limit=1)

            location_dest = self.env['stock.location'].search(
                [('name', '=', 'Запаси'), ('location_id', '=', 'БІРЖА')], limit=1)

            if not location_dest:
                raise ValidationError("Не знайдено локації 'БІРЖА'.")

            location_dest_stock_move = self.env['stock.location'].search(
                [('name', '=', 'Vendors'), ('location_id', '=', 'Partners')], limit=1)

            if not location_dest_stock_move:
                raise ValidationError("Не знайдено локації 'Vendors/Partners'.")

            picking_vals = {
                'partner_id': record.partner_id.id,
                'picking_type_id': picking_type.id,
                'origin': record.invoice_number,
                'location_dest_id': location_dest.id,
                'document_ids': [(6, 0, record.document_ids.ids)],
                'currency_id': record.currency_id.id
            }
            picking = stock_picking_obj.create(picking_vals)

            for move_line in valid_moves:
                move_vals = {
                    'picking_id': picking.id,
                    'product_id': move_line.product_id.id,
                    'product_uom_qty': move_line.quantity,
                    'quantity': move_line.quantity,
                    'name': move_line.product_id.name,
                    'price_unit': move_line.price,
                    'product_uom': move_line.product_id.uom_id.id,
                    'description_picking': move_line.product_id.name,
                    'location_id': location_dest_stock_move.id,
                    'location_dest_id': location_dest.id,
                }
                stock_move_obj.create(move_vals)

            picking.button_validate()

            return {
                'type': 'ir.actions.act_window',
                'name': 'Надходження',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'res_id': picking.id,
                'target': 'current',
            }

        return True


class ReceivingWoodLine(models.Model):
    _name = 'receiving.wood.line'
    _description = 'Receiving Wood Line'

    receiving_wood_id = fields.Many2one(
        'receiving.wood', string="Receiving Wood", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Продукт")
    quantity = fields.Float(string="Кількість", digits=(16, 3))
    currency_id = fields.Many2one(
        'res.currency',
        string="Валюта",
        related='receiving_wood_id.currency_id',
        store=True,
        readonly=True
    )
    price_unit = fields.Monetary(string='Ціна за одиницю')

    price = fields.Monetary(
        string="Ціна",
        # currency_field='currency_id',
        compute='_compute_price',
        store=True
    )

    percentage = fields.Float(
        string="Процент (%)",
        compute="_compute_percentage",
        store=True,
        digits=(16, 2)
    )

    @api.depends('quantity','price_unit')
    def _compute_price(self):
        for record in self:
            # price = record.product_id.lst_price if record.product_id else 0.0
            record.price = record.price_unit * record.quantity

    @api.depends('quantity', 'receiving_wood_id.product_quantity_t')
    def _compute_percentage(self):
        for line in self:
            if line.receiving_wood_id.product_quantity_t > 0:
                line.percentage = (line.quantity / line.receiving_wood_id.product_quantity_t) * 100
            else:
                line.percentage = 0.0
