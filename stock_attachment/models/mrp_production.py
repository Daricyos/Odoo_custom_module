from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    total_raw_material_qty = fields.Float(
        string="Использовано сырья (м³)",
        compute="_compute_total_raw_material_qty",
        store=True,
    )
    waste_ratio = fields.Float(string='Коефіцієнт відходів', compute='_compute_waste_ratio')

    processing_coefficient = fields.Float(
        string="Коэффициент переработки",
        compute="_compute_processing_coefficient",
        store=True,
        digits=(16, 4),
    )

    by_product_qty = fields.Float(
        string="Обсяг побічних продуктів (м³)",
        compute='_compute_by_product_qty',
        store=True
    )

    recycling_rates_config = fields.Float(
        store=True
    )

    @api.depends('move_raw_ids.product_uom_qty', 'product_qty', 'move_byproduct_ids.product_uom_qty')
    def _compute_by_product_qty(self):
        for obj in self:
            obj.by_product_qty = sum(obj.move_raw_ids.mapped('product_uom_qty')) - obj.product_qty

            if obj.move_byproduct_ids:
                # for move in obj.move_byproduct_ids:
                #     move.product_uom_qty = obj.by_product_qty
                obj.by_product_qty = sum(
                    obj.move_byproduct_ids.mapped('product_uom_qty')
                )


    @api.depends('move_raw_ids.product_uom_qty')
    def _compute_total_raw_material_qty(self):
        for production in self:
            production.total_raw_material_qty = sum(
                production.move_raw_ids.mapped('product_uom_qty')
                # production.move_raw_ids.mapped('actual_costs')
            )

    @api.depends('product_qty', 'by_product_qty', 'total_raw_material_qty')
    def _compute_processing_coefficient(self):
        for production in self:
            total_output = production.product_qty + production.by_product_qty

            if production.total_raw_material_qty > 0:
                production.processing_coefficient = (
                        total_output / production.total_raw_material_qty
                )
            else:
                production.processing_coefficient = 0.0

    @api.depends('move_byproduct_ids.actual_costs', 'move_raw_ids.product_uom_qty')
    def _compute_waste_ratio(self):
        for rec in self:
            if rec.by_product_qty > 0.0 and rec.total_raw_material_qty > 0.0:
                rec.waste_ratio = rec.by_product_qty / rec.total_raw_material_qty
            else:
                rec.waste_ratio = 0.0


