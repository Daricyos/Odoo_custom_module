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

    @api.depends('by_product_qty', 'total_raw_material_qty')
    def _compute_waste_ratio(self):
        for rec in self:
            if rec.by_product_qty > 0.0 and rec.total_raw_material_qty > 0.0:
                rec.waste_ratio = rec.by_product_qty / rec.total_raw_material_qty
            else:
                rec.waste_ratio = 0.0

    @api.onchange('move_raw_ids')
    def _change_byproduct_uom_qty(self):
        for rec in self:
            if rec.move_raw_ids and rec.move_byproduct_ids:
                raw_qty = sum(raw.product_uom_qty for raw in rec.move_raw_ids)
                byprod_qty = sum(byprod.product_uom_qty for byprod in rec.move_byproduct_ids)
                byprod_fact = raw_qty - rec.product_qty
                diff = byprod_fact - byprod_qty
                if diff != 0.0:
                    rec.move_byproduct_ids[0].product_uom_qty += diff

    def action_change_product_qty(self):
        for rec in self:
            if rec.move_raw_ids and rec.bom_id:
                for move_raw in rec.move_raw_ids:
                    move_raw_qty = move_raw.product_uom_qty
                    if rec.bom_id.bom_line_ids:
                        for bom_line in rec.bom_id.bom_line_ids:
                            if move_raw.product_id.id == bom_line.product_id.id and rec.bom_id.product_qty > 0 and bom_line.product_qty > 0:
                                prod_qty = move_raw_qty * (rec.bom_id.product_qty / bom_line.product_qty)
                                rec.product_qty = prod_qty
                                break
            # SQL ін'єкція, не використовуєнься
            # new_qty = rec.total_raw_material_qty - rec.by_product_qty
            # rec.env.cr.execute("""
            #     UPDATE mrp_production
            #     SET product_qty = %s
            #     WHERE id = %s
            # """, (new_qty, rec.id))
            # # Оновлюємо кеш
            # # rec.product_qty = new_qty
            # rec.invalidate_recordset(['product_qty'])
            # # import time
            # # time.sleep(1)
            # for raw in rec.move_raw_ids:
            #     raw._compute_actual_costs()
            #     raw._compute_actual_yield_factor()

    def action_force_delete(self):
        """Видаляє виробниче замовлення разом з усіма пов'язаними переміщеннями"""
        for production in self:
            # Збираємо всі пов'язані переміщення
            moves_to_delete = self.env['stock.move']

            # Переміщення сировини (move_raw_ids)
            if production.move_raw_ids:
                moves_to_delete |= production.move_raw_ids

            # Переміщення готової продукції (move_finished_ids)
            if production.move_finished_ids:
                moves_to_delete |= production.move_finished_ids

            # Додаткові переміщення через workorder, якщо є
            if hasattr(production, 'workorder_ids'):
                for workorder in production.workorder_ids:
                    if hasattr(workorder, 'move_raw_ids'):
                        moves_to_delete |= workorder.move_raw_ids
                    if hasattr(workorder, 'move_finished_ids'):
                        moves_to_delete |= workorder.move_finished_ids

            # Обробляємо переміщення
            if moves_to_delete:
                # Спочатку обробляємо stock.move.line для done переміщень
                done_moves = moves_to_delete.filtered(lambda m: m.state == 'done')

                if done_moves:
                    # Знаходимо всі stock.move.line для done переміщень
                    done_move_lines = self.env['stock.move.line'].search([
                        ('move_id', 'in', done_moves.ids)
                    ])

                    # Видаляємо stock valuation layers (бухгалтерські проводки)
                    if done_move_lines:
                        valuation_layers = self.env['stock.valuation.layer'].search([
                            ('stock_move_id', 'in', done_moves.ids)
                        ])
                        if valuation_layers:
                            valuation_layers.sudo().unlink()

                        # Видаляємо account.move (бухгалтерські записи)
                        account_moves = self.env['account.move'].search([
                            ('stock_move_id', 'in', done_moves.ids)
                        ])
                        if account_moves:
                            account_moves.sudo().unlink()

                    # Змінюємо статус done переміщень на draft через sudo
                    done_moves.sudo().write({'state': 'draft'})

                    # Видаляємо move lines
                    if done_move_lines:
                        done_move_lines.sudo().unlink()

                # Тепер скасовуємо всі переміщення що не в draft
                non_draft_moves = moves_to_delete.filtered(lambda m: m.state != 'draft')
                if non_draft_moves:
                    non_draft_moves.sudo().write({'state': 'draft'})

                # Видаляємо всі move lines
                all_move_lines = self.env['stock.move.line'].search([
                    ('move_id', 'in', moves_to_delete.ids)
                ])
                if all_move_lines:
                    all_move_lines.sudo().unlink()

                # Видаляємо самі переміщення
                moves_to_delete.sudo().unlink()

            # Видаляємо workorder, якщо є
            if hasattr(production, 'workorder_ids') and production.workorder_ids:
                production.workorder_ids.sudo().unlink()

            # Видаляємо саме виробниче замовлення через sudo без зміни статусу
            production.sudo().write({'state': 'cancel'})
            production.sudo().unlink()

            self.env['bus.bus']._sendone(
                self.env.user.partner_id,
                'simple_notification',
                {
                    'type': 'success',
                    'message':  _('Виробничі замовлення та всі пов\'язані переміщення видалено'),
                    'sticky': False,
                }
            )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Виробничі замовлення'),
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'target': 'current',
        }