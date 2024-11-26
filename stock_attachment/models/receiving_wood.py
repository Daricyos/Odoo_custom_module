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
    documents_ids = fields.One2many('ir.attachment', 'wood_line', string='Завантажити')

    @api.constrains('documents_ids')
    def _check_file_type(self):
        for record in self:
            for attachment in record.documents_ids:
                # Отримуємо розширення файлу
                file_ext = os.path.splitext(attachment.name)[1].lower()
                # Визначаємо дозволені розширення
                allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png']

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
            print(valid_moves)

            if not valid_moves:
                raise ValidationError("Не знайдено продуктів з кількістю більше 0.")

            picking_type = self.env['stock.picking.type'].search([('name', '=', 'Надходження')],
                                                                 limit=1)

            location_dest = self.env['stock.location'].search([('name', '=', 'Запаси')], limit=1)
            if not location_dest:
                raise ValidationError("Не знайдено локації 'СИРОВ/Запаси'.")

            picking_vals = {
                'partner_id': record.partner_id.id,
                'picking_type_id': picking_type.id,  # Замените на ваш picking_type_id
                'origin': record.invoice_number,
                'location_dest_id': location_dest.id,
                'document_ids': [(6, 0, record.documents_ids.ids)],
            }
            picking = stock_picking_obj.create(picking_vals)

            for move_line in valid_moves:
                print(move_line.product_id.name)
                move_vals = {
                    'picking_id': picking.id,
                    'product_id': move_line.product_id.id,
                    'product_uom_qty': move_line.quantity,
                    'quantity': move_line.quantity,
                    'name': move_line.product_id.name,
                    'product_uom': move_line.product_id.uom_id.id,
                    'location_id': location_dest.id,
                    'location_dest_id': location_dest.id,
                }
                stock_move_obj.create(move_vals)

            picking.action_confirm()
            picking.action_assign()
            picking.button_validate()

            return {
                'type': 'ir.actions.act_window',
                'name': 'Надходження',  # Имя окна
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'res_id': picking.id,  # Открываем созданную запись
                'target': 'current',  # Открывать в текущем окне
            }

        return True


class ReceivingWoodLine(models.Model):
    _name = 'receiving.wood.line'
    _description = 'Receiving Wood Line'

    receiving_wood_id = fields.Many2one(
        'receiving.wood', string="Receiving Wood", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Продукт")
    quantity = fields.Float(string="Кількість")


class IrAttachmentWoodLine(models.Model):
    _inherit = 'ir.attachment'

    wood_line = fields.Many2one('receiving.wood')