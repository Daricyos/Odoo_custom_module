from odoo import models, fields, api


class ResPartnerWood(models.Model):
    _inherit = 'res.partner'

    driver_license_number = fields.Char(string="Номер Номер водійського посвідчення")
    vehicle_number = fields.Char(string="Транспортный засіб (номер)")
