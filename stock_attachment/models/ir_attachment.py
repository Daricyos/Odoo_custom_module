# models/ir_attachment.py
import base64

from odoo import models, fields, api
from odoo.exceptions import UserError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def action_preview_image(self):
        """Відкрити модальне вікно з прев'ю зображення"""
        self.ensure_one()  # Працюємо тільки з одним записом
        return {
            'type': 'ir.actions.act_window',
            'name': 'Image Preview',
            'res_model': 'ir.attachment',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('stock_attachment.view_attachment_preview_form').id,
            'target': 'new',  # Модальне вікно
        }

    def action_download_file(self):
        if not self.datas:
            raise UserError("Файл відсутній.")

        # Створення тимчасового вкладення
        attachment = self.env['ir.attachment'].create({
            'name': self.name,
            'datas': self.datas,
            'res_model': self._name,
            'res_id': self.id
        })

        # Повернення дії завантаження
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self'
        }