from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import os



class ReceivingWood(models.Model):
    _name = 'receiving.wood'
    _description = 'Receiving Wood'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'


    name = fields.Char(string='Назва', default='Без назви', compute='_compute_name', store=True)
    state = fields.Selection(
        string='Статус',
        selection=[
            ('draft', 'Чернетка'),
            ('done','Прийнято')
        ],
        default='draft',
        tracking=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Отримати з',
        required=True,
        domain="[('category_id.name', '=', 'Постачальник')]",
        tracking=True
    )
    driver_license_number = fields.Char(
        string="Номер водійського посвідчення",
        compute='_compute_driver_info',
        store=True
    )
    vehicle_number = fields.Char(
        string="Транспортный засіб (номер)",
        compute='_compute_driver_info',
        store=True
    )
    stock_picking_id = fields.Many2one(
        'stock.picking',
        string='Переміщення',
        tracking=True
    )

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Купівля',
        tracking=True
    )

    invoice_number = fields.Integer(
        'Номер накладної',
        required=True,
        tracking=True
    )

    move_ids_without_package = fields.One2many(
        'receiving.wood.line',
        'receiving_wood_id',
        string="Stock move"
    )

    product_quantity_t = fields.Float(
        compute='_compute_total_move_quantity',
        string='Загальна м³',
        store=True,
        digits=(16, 3),
        tracking=True
    )

    document_ids = fields.Many2many(
        'ir.attachment',
        string='Завантажити документи',
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Валюта",
        required=True,
        tracking=True
    )

    total_price = fields.Monetary(
        'Ціна',
        currency_field='currency_id',
        compute='_compute_total_price',
        stor=True,
        tracking=True
    )

    @api.depends('partner_id')
    def _compute_driver_info(self):
        for rec in self:
            if rec.partner_id:
                rec.driver_license_number = rec.partner_id.driver_license_number
                rec.vehicle_number = rec.partner_id.vehicle_number
            else:
                rec.driver_license_number = ''
                rec.vehicle_number = ''

    @api.depends('partner_id', 'create_date')
    def _compute_name(self):
        for rec in self:
            if rec.partner_id:
                # # Форматуємо як "ДД.ММ.РРРР ГГ:ХХ"
                # date_str = rec.create_date.strftime('%d.%m.%Y %H:%M') if rec.create_date else ''
                # rec.name = f'{rec.partner_id.name}/{date_str}'
                if rec.create_date:
                    local_date = fields.Datetime.context_timestamp(rec, rec.create_date)
                    date_str = local_date.strftime('%d.%m.%Y %H:%M')
                else:
                    date_str = ''
                rec.name = f'{rec.partner_id.name}/{date_str}'
            else:
                rec.name = 'Без назви'

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

    def action_create_p_order_and_s_picking(self):
        purchase_order_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']

        for record in self:
            # Перевірка наявності продуктів з кількістю > 0
            valid_moves = record.move_ids_without_package.filtered(lambda line: line.quantity > 0)

            if not valid_moves:
                raise ValidationError("Не знайдено продуктів з кількістю більше 0.")

            # Перевірка наявності постачальника
            if not record.partner_id:
                raise ValidationError("Не вказано постачальника.")

            # Пошук складу для надходження
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'incoming'),
                ('warehouse_id', '!=', False)
            ], limit=1)

            if not picking_type:
                raise ValidationError("Не знайдено типу операції для надходження.")

            # Створення замовлення на купівлю
            po_vals = {
                'partner_id': record.partner_id.id,
                'origin': record.name or '',
                'currency_id': record.currency_id.id if record.currency_id else record.partner_id.currency_id.id,
                'picking_type_id': picking_type.id,
                'date_order': fields.Datetime.now(),
                'invoice_number': record.invoice_number,
                # Додаткові поля, якщо потрібно
                # 'payment_term_id': record.partner_id.property_supplier_payment_term_id.id,
                # 'fiscal_position_id': record.partner_id.property_account_position_id.id,
            }

            purchase_order = purchase_order_obj.create(po_vals)

            # Створення рядків замовлення
            for move_line in valid_moves:
                # Пошук інформації про постачальника для продукту
                seller = move_line.product_id._select_seller(
                    partner_id=record.partner_id,
                    quantity=move_line.quantity,
                    uom_id=move_line.product_id.uom_po_id
                )

                po_line_vals = {
                    'order_id': purchase_order.id,
                    'product_id': move_line.product_id.id,
                    'name': move_line.product_id.display_name or move_line.product_id.name,
                    'product_qty': move_line.quantity,
                    'product_uom': move_line.product_id.uom_po_id.id,
                    'price_unit': move_line.price_unit if hasattr(move_line, 'price_unit') else 0.0,
                    'date_planned': fields.Datetime.now(),
                    'taxes_id': [(6, 0, move_line.product_id.supplier_taxes_id.ids)],
                }

                purchase_order_line_obj.create(po_line_vals)

            # Оновлення стану запису
            if purchase_order:
                record.purchase_order_id = purchase_order.id  # Додайте поле purchase_order_id до моделі
                # record.state = 'po_created'  # або інший стан
                purchase_order.button_confirm()
                picking = self.purchase_order_id.picking_ids[0] if self.purchase_order_id.picking_ids else False

                if picking:

                    picking.write(
                        {
                            'document_ids': [(6, 0, record.document_ids.ids)],
                            'invoice_number': record.invoice_number
                        }
                    )
                    # Валідуємо надходження
                    picking.button_validate()
                    self.stock_picking_id = picking.id
                    self.state = 'done'

                    # Повернення форми надходження, якщо потрібно
                    # return {
                    #     'type': 'ir.actions.act_window',
                    #     'name': 'Надходження',
                    #     'res_model': 'stock.picking',
                    #     'view_mode': 'form',
                    #     'res_id': picking.id,
                    #     'target': 'current',
                    # }

            # Повернення форми створеного замовлення
            return {
                'type': 'ir.actions.act_window',
                'name': 'Замовлення на купівлю',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': purchase_order.id,
                'target': 'current',
            }

        return True

    # Не використовується
    def action_create_stock_picking(self):
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
                    # 'price_unit': move_line.price,
                    'price_unit': move_line.price_unit,
                    'product_uom': move_line.product_id.uom_id.id,
                    'description_picking': move_line.product_id.name,
                    'location_id': location_dest_stock_move.id,
                    'location_dest_id': location_dest.id,
                }
                stock_move_obj.create(move_vals)

            picking.button_validate()

            if picking:
                record.stock_picking_id = picking.id
                record.state = 'done'

            return {
                'type': 'ir.actions.act_window',
                'name': 'Надходження',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'res_id': picking.id,
                'target': 'current',
            }

        return True

    def action_view_picking(self):
        """
        Smart button для перегляду надходження
        """
        self.ensure_one()
        if self.stock_picking_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'res_id': self.stock_picking_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            raise UserError('Немає надходження.')

    def action_view_purchase(self):
        """
        Smart button для перегляду надходження
        """
        self.ensure_one()
        if self.purchase_order_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'res_id': self.purchase_order_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            raise UserError('Немає купівлі.')


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
