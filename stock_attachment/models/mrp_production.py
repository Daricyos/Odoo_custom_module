from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # move_byproduct_ids = fields.One2many(
    #     'stock.move',
    #     compute='_compute_move_byproduct_ids',
    #     inverse='_set_move_byproduct_ids',
    #     store=True
    # )
    total_raw_material_qty = fields.Float(
        string="Использовано сырья (м³)",
        compute="_compute_total_raw_material_qty",
        store=True,
    )
    waste_ratio = fields.Float(string='Коефіцієнт відходів', compute='_compute_waste_ratio')

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

    by_product_qty = fields.Float(compute='_compute_by_product_qty', store=True)

    recycling_rates_config = fields.Float(
        store=True
    )

    @api.model
    def create(self, vals):
        production = super(MrpProduction, self).create(vals)

        for move in production.move_raw_ids:
            if move.actual_costs is None or move.actual_costs <= 0:
                raise ValidationError(_("Поле 'Фактичні витрати' є обов'язковим і має бути більше нуля."))

        return production

    @api.depends('move_raw_ids.actual_costs', 'product_qty')
    def _compute_by_product_qty(self):
        for obj in self:
            obj.by_product_qty = sum(obj.move_raw_ids.mapped('actual_costs')) - obj.product_qty

            if obj.move_byproduct_ids:
                for move in obj.move_byproduct_ids:
                    move.product_uom_qty = obj.by_product_qty


    @api.depends('move_raw_ids.product_uom_qty')
    def _compute_total_raw_material_qty(self):
        for production in self:
            production.total_raw_material_qty = sum(
                # production.move_raw_ids.mapped('product_uom_qty')
                production.move_raw_ids.mapped('actual_costs')
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

    @api.depends('move_byproduct_ids.actual_costs', 'move_raw_ids.product_uom_qty')
    def _compute_waste_ratio(self):
        for rec in self:
            if rec.total_byproduct_qty > 0.0 and rec.total_raw_material_qty > 0.0:
                rec.waste_ratio = rec.total_byproduct_qty / rec.total_raw_material_qty
            else:
                rec.waste_ratio = 0.0

    # @api.depends('move_byproduct_ids.actual_costs','move_raw_ids.product_uom_qty')
    # def _compute_waste_ratio(self):
    #     for rec in self:
    #         if rec.move_byproduct_ids and rec.move_raw_ids:
    #             # actual_costs = sum(prod.actual_costs for prod in rec.move_byproduct_ids)
    #             actual_costs = sum(rec.move_byproduct_ids.mapped('actual_costs'))
    #             # product_uom_qty = sum(raw.product_uom_qty for raw in rec.move_raw_ids)
    #             product_uom_qty = sum(rec.move_raw_ids.mapped('product_uom_qty'))
    #             if actual_costs > 0.0 and product_uom_qty > 0.0:
    #                 rec.waste_ratio = product_uom_qty / actual_costs
    #             else:
    #                 rec.waste_ratio = 0.0
    #         else:
    #             rec.waste_ratio = 0.0

