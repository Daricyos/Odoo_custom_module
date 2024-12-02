from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ChopLogs(models.Model):
    _name = "chop.logs"
    _description = "Chopping Logs"

    responsible = fields.Many2one('res.users', string='Відповідальний', default=lambda self: self.env.user)
    steamed_bich_A = fields.Float(string="Бук Пропарений A")
    steamed_bich_B = fields.Float(string="Бук Пропарений B")
    steamed_bich_C = fields.Float(string="Бук Пропарений C")
    steamed_bich_D = fields.Float(string="Бук Пропарений D")
    partner_id = fields.Many2one(
        'res.partner',
        'Отримати з',
        required=True
    )

class ReceivingBlocks(models.Model):
    _name = "receiving.blocks"
    _description = "Receiving Blocks"

    partner_id = fields.Many2one(
        'res.partner',
        'Отримати з',
        required=True,
        domain="[('category_id.name', '=', 'Постачальник')]"
    )

class BlocksDrying(models.Model):
    _name = "blocks.drying"
    _description = "Block Drying"

    partner_id = fields.Many2one(
        'res.partner',
        'Отримати з',
        required=True,
        domain="[('category_id.name', '=', 'Постачальник')]"
    )

class ReceivingDryBlocks(models.Model):
    _name = "receiving.dry.blocks"
    _description = "Receiving Dry Blocks"

    partner_id = fields.Many2one(
        'res.partner',
        'Отримати з',
        required=True,
        domain="[('category_id.name', '=', 'Постачальник')]"
    )

    class BlocksPeeling(models.Model):
        _name = "blocks.peeling"
        _description = "Block Peeling"

        partner_id = fields.Many2one(
            'res.partner',
            'Отримати з',
            required=True,
            domain="[('category_id.name', '=', 'Постачальник')]"
        )