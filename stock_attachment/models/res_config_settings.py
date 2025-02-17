from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    recycling_rates = fields.Float(string='Коефіцієнт переробки', config_parameter='stock_attachment.recycling_rates')
    minimum_stock = fields.Integer(string='Мінімальний запас', config_parameter='stock_attachment.minimum_stock')
