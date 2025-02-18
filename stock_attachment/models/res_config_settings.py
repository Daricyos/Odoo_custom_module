from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    recycling_rates = fields.Float(string='Коефіцієнт переробки', config_parameter='stock_attachment.recycling_rates')
    minimum_stock = fields.Float(string='Мінімальний запас', config_parameter='stock_attachment.minimum_stock')

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        recycling_rates = self.recycling_rates
        minimum_stock = self.minimum_stock
        self.env['mrp.production'].search([]).write({'recycling_rates_config': recycling_rates})
        self.env['product.product'].search([]).write({'minimum_stock_config': minimum_stock})
