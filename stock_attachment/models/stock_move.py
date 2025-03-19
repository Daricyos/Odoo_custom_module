from odoo import api, fields, models


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    actual_costs = fields.Float('Фактичні витрати', digits=(16, 3), required=True)
    actual_yield_factor = fields.Float('Фактичний коефіцієнт виходу', compute="_compute_actual_yield_factor", store=True)

    @api.depends('raw_material_production_id.product_qty', 'actual_costs')
    def _compute_actual_yield_factor(self):
        for record in self:
            print(record.raw_material_production_id.product_qty)
            if record.raw_material_production_id.product_qty > 0 and record.actual_costs != 0:
                record.actual_yield_factor = (record.raw_material_production_id.product_qty / record.actual_costs) * 100
            else:
                record.actual_yield_factor = 0
