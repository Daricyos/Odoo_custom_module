import base64

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import os


class StockPicking(models.Model):
    _inherit = 'stock.picking'

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
    currency_id = fields.Many2one('res.currency', string="Валюта",  default=lambda self: self._get_default_currency())

    def _get_default_currency(self):
        return self.env.context.get('default_currency_id') or self.env.company.currency_id.id

    total_price = fields.Monetary('Ціна', currency_field='currency_id', compute='_compute_total_price')
    document_ids = fields.Many2many('ir.attachment', string='Завантажити документи')
    product_quantity_t = fields.Float(compute='_compute_total_move_quantity', store=True, digits=(16, 3))

    @api.depends('partner_id')
    def _compute_driver_info(self):
        for rec in self:
            if rec.partner_id:
                rec.driver_license_number = rec.partner_id.driver_license_number
                rec.vehicle_number = rec.partner_id.vehicle_number
            else:
                rec.driver_license_number = ''
                rec.vehicle_number = ''


    @api.depends('move_ids_without_package.price_unit')
    def _compute_total_price(self):
        for obj in self:
            # obj.total_price = sum(obj.move_ids_without_package.mapped('price_unit'))
            obj.total_price = sum(move.price_unit * move.quantity for move in obj.move_ids_without_package)

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

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.model
    def action_receiving_wood(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Надходження деревини',
            'res_model': 'receiving.wood',
            'view_mode': 'form',
        }


class StockPickingLine(models.Model):
    _inherit = 'stock.move.line'

    partner_id = fields.Char(related='move_id.partner_id.name', store=True, related_sudo=False, readonly=False)