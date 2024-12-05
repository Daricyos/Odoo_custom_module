from odoo import models, fields, api


class RawMaterialsReportWizard(models.TransientModel):
    _name = 'raw.materials.report.wizard'
    _description = 'Майстер звіту про сировину'

    start_date = fields.Date(string='Дата з', required=True)
    end_date = fields.Date(string='Дата до', required=True)



    # @api.model
    # def get_data(self):
    #     data = self.env.ref('raw_materials_report.data').data(self)
    #     return {
    #         'doc_model': 'raw.materials.report.wizard',
    #         'data': data,
    #     }

    def action_gen_report(self):
        report_action = self.env.ref('raw_materials_report.raw_materials_report_action').report_action(self)
        return report_action



# from odoo import models, fields, api
# from collections import defaultdict
#
# class RawMaterialsReportWizard(models.TransientModel):
#     _name = 'raw.materials.report.wizard'
#     _description = 'Майстер звіту про сировину'
#
#     date_from = fields.Date(string='Дата з', required=True)
#     date_to = fields.Date(string='Дата до', required=True)
#
#     def _fetch_moves(self):
#         """Метод для отримання переміщень на основі вибраного періоду."""
#         warehouse = self.env['stock.warehouse'].search([
#             ('name', 'ilike', 'Прийом Сировини')
#         ], limit=1)
#
#         moves = []
#         if warehouse:
#             moves = self.env['stock.move'].search([
#                 ('location_dest_id', '=', warehouse.lot_stock_id.id),
#                 ('state', '=', 'done'),
#                 ('date', '>=', self.date_from),
#                 ('date', '<=', self.date_to)
#             ])
#         return moves
#
#     def process_report_data(self, moves):
#         """Метод для обробки переміщень і створення звіту."""
#         report_data_grouped = defaultdict(list)
#         for move in moves:
#             reference = move.reference or 'N/A'
#             report_data_grouped[reference].append({
#                 'date': move.date,
#                 'product': move.product_id.name,
#                 'quantity': move.product_uom_qty,
#                 'uom': move.product_uom.name,
#                 'comp': move.partner_id.commercial_company_name,
#                 'partner': move.partner_id.name or 'N/A',
#                 'reference': reference
#             })
#
#         processed_report_data = []
#         total_quantities = defaultdict(float)
#         total_overall_quantity = 0
#
#         product_mapping = {
#             "Бук сорт A": "pichA",
#             "Бук сорт B": "pichB",
#             "Бук сорт C": "pichC",
#             "Бук сорт D": "pichD"
#         }
#
#         for reference, group in report_data_grouped.items():
#             product_quantities = defaultdict(float)
#             for move in group:
#                 product_name = move['product']
#                 quantity = move['quantity']
#
#                 if product_name in product_mapping:
#                     total_quantities[product_mapping[product_name]] += quantity
#                     total_overall_quantity += quantity
#                     product_quantities[product_name] += quantity
#
#             processed_item = {
#                 'date': group[0]['date'],
#                 'comp': group[0]['comp'],
#                 'partner': group[0]['partner'],
#                 'pichA': product_quantities.get("Бук сорт A", 0),
#                 'pichB': product_quantities.get("Бук сорт B", 0),
#                 'pichC': product_quantities.get("Бук сорт C", 0),
#                 'pichD': product_quantities.get("Бук сорт D", 0),
#                 'reference': reference,
#                 'quantity': sum(product_quantities.values())
#             }
#
#             processed_report_data.append(processed_item)
#
#         summary = {
#             'total_quantities': dict(total_quantities),
#             'total_overall_quantity': total_overall_quantity
#         }
#
#         return processed_report_data, summary
#
#     def action_gen_report(self):
#         """Генеруємо звіт на основі вказаних дат."""
#         moves = self._fetch_moves()
#         processed_report_data, summary = self.process_report_data(moves)
#
#         # Виклик звіту із зібраними даними
#         report_action = self.env.ref('raw_materials_report.raw_materials_report_action').report_action(self, data={
#             'processed_report_data': processed_report_data,
#             'summary': summary
#         })
#         return report_action
#













    # line_ids = fields.One2many(
    #     'raw.materials.report.line',
    #     'wizard_id',
    #     string='Деталі звіту'
    # )

    # @api.model
    # def data_report(self):
    #     data = self.env.ref('raw_materials_report.data').data(self)
    #     return data
    #
    # data = data_report
    #     {
    #
    #         'doc_model': 'raw.materials.report.wizard',
    #         'data': data,
    #         # 'data': report_data,
    #     }





# class RawMaterialsReportLine(models.TransientModel):
#     _name = 'raw.materials.report.line'
#     _description = 'Raw Materials Report Line'
#
#     wizard_id = fields.Many2one('raw.materials.report.wizard', string='Звіт')
#     date = fields.Date(string='Дата')
#     comp = fields.Char(string='Постачальник')
#     partner = fields.Char(string='Водій')
#     quantity = fields.Float(string='Об\'єм (м3)')
#     pichA = fields.Float(string='Сорт A')
#     pichB = fields.Float(string='Сорт B')
#     pichC = fields.Float(string='Сорт C')
#     pichD = fields.Float(string='Сорт D')
