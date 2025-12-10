from odoo import api, fields, models


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    actual_costs = fields.Float(
        'Норма витрати сировини',
        digits=(16, 3),
        compute='_compute_actual_costs',
        store=True
        # required=True,
        # default=None
        )
    actual_yield_factor = fields.Float('Фактичний коефіцієнт виходу', compute="_compute_actual_yield_factor", store=True)

    @api.depends('raw_material_production_id.product_qty', 'product_uom_qty')
    def _compute_actual_yield_factor(self):
        for record in self:
            if record.raw_material_production_id.product_qty > 0 and record.product_uom_qty != 0:
                # record.actual_yield_factor = (record.raw_material_production_id.product_qty / record.actual_costs) * 100
                record.actual_yield_factor = record.raw_material_production_id.product_qty / record.product_uom_qty
            else:
                record.actual_yield_factor = 0

    @api.depends('raw_material_production_id.product_qty', 'raw_material_production_id.bom_id')
    def _compute_actual_costs(self):
        for record in self:
            if record.raw_material_production_id.product_qty > 0 and record.raw_material_production_id.bom_id:
                for bom_line in record.raw_material_production_id.bom_id.bom_line_ids:
                    if bom_line.product_id.id == record.product_id.id:
                        # print(f"{record.actual_costs=} = {record.raw_material_production_id.product_qty=} * {bom_line.product_qty=} / {record.raw_material_production_id.bom_id.product_qty=}")
                        # record.actual_costs = record.raw_material_production_id.product_qty * bom_line.product_qty / record.raw_material_production_id.bom_id.product_qty
                        record.actual_costs = record.raw_material_production_id.product_uom_id._compute_quantity(
                            record.raw_material_production_id.product_qty * bom_line.product_qty / record.raw_material_production_id.bom_id.product_qty,
                            bom_line.product_id.uom_id
                        )
                    else:
                        record.actual_costs = 0
                    # print(f'{record.actual_costs=}')
                    # print(f'{record.product_uom_qty=}')
            else:
                record.actual_costs = 0




    # @api.onchange('actual_costs')
    # def _onchange_actual_costs(self):
    #     if self.actual_costs:
    #         self.product_uom_qty = self.actual_costs
