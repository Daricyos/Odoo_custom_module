from odoo import api, fields, models


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    def _get_action_view_picking(self, pickings):
        self.ensure_one()
        # Записываем значения в запись, исключая picking_type_id
        vals = {
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'currency_id': self.currency_id.id,
        }
        pickings.write(vals)  # Обновляем записи
        result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        result['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_origin': self.name,
            'default_picking_type_id': self.picking_type_id.id,
            'default_currency_id': self.currency_id.id
        }
        if not pickings or len(pickings) > 1:
            result['domain'] = [('id', 'in', pickings.ids)]
        elif len(pickings) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            result['views'] = form_view + [(state, view) for state, view in result.get('views', []) if view != 'form']
            result['res_id'] = pickings.id
        return result