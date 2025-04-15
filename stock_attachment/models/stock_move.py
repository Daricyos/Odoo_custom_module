from odoo import api, fields, models


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    actual_costs = fields.Float('Фактичні витрати', digits=(16, 3), required=True, default=None)
    actual_yield_factor = fields.Float('Фактичний коефіцієнт виходу', compute="_compute_actual_yield_factor", store=True)

    @api.depends('raw_material_production_id.product_qty', 'actual_costs')
    def _compute_actual_yield_factor(self):
        for record in self:
            if record.raw_material_production_id.product_qty > 0 and record.actual_costs != 0:
                record.actual_yield_factor = (record.raw_material_production_id.product_qty / record.actual_costs) * 100
            else:
                record.actual_yield_factor = 0


    @api.onchange('actual_costs')
    def _onchange_actual_costs(self):
        if self.actual_costs:
            self.product_uom_qty = self.actual_costs
