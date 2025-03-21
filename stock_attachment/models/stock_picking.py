import base64

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import os


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    document_ids = fields.Many2many('ir.attachment', string='Завантажити документи')
    product_quantity_t = fields.Float(compute='_compute_total_move_quantity', store=True, digits=(16, 3))

    @api.depends('move_ids_without_package.product_uom_qty')
    def _compute_total_move_quantity(self):
        for picking in self:
            picking.product_quantity_t = sum(picking.move_ids_without_package.mapped('product_uom_qty'))

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
# //////////////////////
#     --------Валідація mietype---------------
#     @api.constrains('document_ids')
#     def _check_documents(self):
#         max_size = 25 * 1024 * 1024  # 25MB
#         allowed_types = ['image/jpeg', 'image/png', 'image/svg', 'image/jpg','text/plain', 'application/pdf', 'application/doc', 'application/docx', 'application/xls', 'application/xlsx']
#         for attachment in self.document_ids:
#             if attachment.mimetype not in allowed_types:
#                 raise ValidationError(
#                     f'Файл "{attachment.name}" має недопустиме розширення. '
#                     f'Дозволені формати: {", ".join(allowed_types)}'
#                 )
#             if attachment.file_size > max_size:
#                  raise ValidationError(
#                     f'Файл "{attachment.name}" завеликий. '
#                     f'Максимальний розмір файлу: 25MB')man

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.model
    def action_receiving_wood(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Надходження деревени',
            'res_model': 'receiving.wood',
            'view_mode': 'form',
        }