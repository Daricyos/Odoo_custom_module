from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    total_raw_material_qty = fields.Float(
        string="Использовано сырья (м³)",
        compute="_compute_total_raw_material_qty",
        store=True,
    )

    total_byproduct_qty = fields.Float(
        string="Обсяг побічних продуктів (м³)",
        compute="_compute_total_byproduct_qty",
        store=True,
    )

    processing_coefficient = fields.Float(
        string="Коэффициент переработки",
        compute="_compute_processing_coefficient",
        store=True,
        digits=(16, 4),
    )

    # by_product_qty = fields.Float(compute='_compute_by_product_qty', store=True,)

    recycling_rates_config = fields.Float(
        store=True
    )
    #
    # @api.depends('move_raw_ids.actual_costs', 'product_qty')
    # def _compute_by_product_qty(self):
    #     for obj in self:
    #         obj.by_product_qty = obj.move_raw_ids.actual_costs - obj.product_qty


    @api.depends('move_raw_ids.product_uom_qty')
    def _compute_total_raw_material_qty(self):
        for production in self:
            production.total_raw_material_qty = sum(
                production.move_raw_ids.mapped('product_uom_qty')
            )

    @api.depends('move_byproduct_ids.product_uom_qty')
    def _compute_total_byproduct_qty(self):
        for production in self:
            production.total_byproduct_qty = sum(
                production.move_byproduct_ids.mapped('product_uom_qty')
            )

    @api.depends('product_qty', 'total_byproduct_qty', 'total_raw_material_qty')
    def _compute_processing_coefficient(self):
        for production in self:
            total_output = production.product_qty + production.total_byproduct_qty

            if production.total_raw_material_qty > 0:
                production.processing_coefficient = (
                        total_output / production.total_raw_material_qty
                )
            else:
                production.processing_coefficient = 0.0