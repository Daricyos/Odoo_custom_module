from odoo import models, api
import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict


class RawMaterialsReport(models.AbstractModel):
    _name = 'report.raw_materials_report.report_template'
    _description = 'Звіт про прийом сировини'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['raw.materials.report.wizard']
        report = report_obj.browse(docids)

        # Отримуємо перший день поточного місяця
        first_day = datetime.date.today().replace(day=1)
        # Отримуємо перший день наступного місяця
        next_month = first_day + relativedelta(months=1)

        # Знаходимо склад "Прийом сировини"
        warehouse = self.env['stock.warehouse'].search([
            ('name', 'ilike', 'Прийом Сировини')
        ], limit=1)

        moves = []
        if warehouse:
            # Отримуємо всі переміщення на цей склад за поточний місяць
            moves = self.env['stock.move'].search([
                ('location_dest_id', '=', warehouse.lot_stock_id.id),
                ('state', '=', 'done'),
                ('date', '>=', first_day),
                ('date', '<', next_month)
            ])

        report_data = []
        for move in moves:
            report_data.append({
                'date': move.date,
                'product': move.product_id.name,
                'quantity': move.product_uom_qty,
                'uom': move.product_uom.name,
                'comp':move.partner_id.commercial_company_name,
                'partner': move.partner_id.name or 'N/A',
                'reference': move.reference
            })
        report_data_grouped = {}
        for move in moves:
            reference = move.reference
            if reference not in report_data_grouped:
                report_data_grouped[reference] = []

            report_data_grouped[reference].append({
                'date': move.date,
                'product': move.product_id.name,
                'quantity': move.product_uom_qty,
                'uom': move.product_uom.name,
                'comp': move.partner_id.commercial_company_name,
                'partner': move.partner_id.name or 'N/A',
                'reference': move.reference
            })

        def process_report_data(report_data_grouped):
            processed_report_data = []
            total_quantities = defaultdict(float)
            total_overall_quantity = 0

            # Словник для зіставлення назв продуктів
            product_mapping = {
                "Бук сорт A": "pichA",
                "Бук сорт B": "pichB",
                "Бук сорт C": "pichC",
                "Бук сорт D": "pichD"
            }

            # Перший прохід - підрахунок загальної кількості кожного продукту
            for reference, group in report_data_grouped.items():
                for move in group:
                    product_name = move['product']
                    quantity = move['quantity']

                    if product_name in product_mapping:
                        total_quantities[product_mapping[product_name]] += quantity
                        total_overall_quantity += quantity

            # Другий прохід - створення деталізованих записів
            for reference, group in report_data_grouped.items():
                product_quantities = defaultdict(float)
                for move in group:
                    product_quantities[move['product']] += move['quantity']

                processed_item = {
                    'date': group[0]['date'],
                    'comp': group[0]['comp'],
                    'partner': group[0]['partner'],
                    'pichA': product_quantities.get("Бук сорт A", 0),
                    'pichB': product_quantities.get("Бук сорт B", 0),
                    'pichC': product_quantities.get("Бук сорт C", 0),
                    'pichD': product_quantities.get("Бук сорт D", 0),
                    'reference': reference,
                    'quantity': sum(product_quantities.values())
                }

                processed_report_data.append(processed_item)

            # Формування об'єкту статистики
            summary = {
                'total_quantities': dict(total_quantities),
                'total_overall_quantity': total_overall_quantity
            }

            return processed_report_data, summary

        # Виклик функції
        processed_report_data, summary = process_report_data(report_data_grouped)

        # Приклад використання
        # print("Оброблені дані:", processed_report_data)
        # print("\nЗагальна статистика:")
        # print("Кількість по кожному продукту:", summary['total_quantities'])
        # print("Загальна кількість:", summary['total_overall_quantity'])

        return {
            'doc_ids': docids,
            'doc_model': 'raw.materials.report.wizard',
            'docs': report,
            'data': [processed_report_data,summary],
            # 'data': report_data,
            'datetime': datetime,
        }


class RawMaterialsReportWizard(models.TransientModel):
    _name = 'raw.materials.report.wizard'
    _description = 'Майстер звіту про прийом сировини'
    