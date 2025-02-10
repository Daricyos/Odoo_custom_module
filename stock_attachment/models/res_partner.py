from odoo import models, fields, api


class ResPartnerWood(models.Model):
    _inherit = 'res.partner'

    driver_license_number = fields.Char(string="Номер водительского удостоверения")
    vehicle_number = fields.Char(string="Транспортный засіб (номер)")
