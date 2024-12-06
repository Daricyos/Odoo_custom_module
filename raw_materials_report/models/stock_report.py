from odoo import models, api, fields
import datetime
from collections import defaultdict
from odoo.exceptions import ValidationError


class RawMaterialsReport(models.AbstractModel):
    _name = 'report.raw_materials_report.report_template'
    _description = 'Звіт про прийом сировини'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['raw.materials.report.wizard']
        report = report_obj.browse(docids)

        # Отримуємо початкову та кінцеву дату з полів звіту
        start_date = report.start_date
        end_date = report.end_date

        if not start_date or not end_date:
            raise ValidationError("Будь ласка, вкажіть початок і кінець періоду.")

        if start_date > end_date:
            raise ValidationError("Дата початку не може бути пізнішою за дату завершення.")

        # Знаходимо склад "Прийом сировини"
        warehouse = self.env['stock.warehouse'].search([
            ('name', 'ilike', 'Прийом Сировини')
        ], limit=1)

        moves = []
        if warehouse:
            # Отримуємо всі переміщення на цей склад за вибраний період
            moves = self.env['stock.move'].search([
                ('location_dest_id', '=', warehouse.lot_stock_id.id),
                ('state', '=', 'done'),
                ('date', '>=', start_date),
                ('date', '<=', end_date)
            ],order='date ASC')
        companies = set() # Використовуємо множину, щоб уникнути дублікатів компаній
        responsible_users = set()  # Множина для унікальних відповідальних осіб
        report_data_grouped = {}
        for move in moves:
            responsible_user = move.create_uid.name  # Або move.responsible_id.name, якщо використовуєте інше поле
            partner = move.partner_id
            reference = move.reference
            if reference not in report_data_grouped:
                report_data_grouped[reference] = []
            # print("Move Fields:", move.read())
            report_data_grouped[reference].append({
                'date': move.date or 'N/A',
                'product': move.product_id.name or 'N/A',
                'quantity': move.product_uom_qty or 0,
                'uom': move.product_uom.name or 'N/A',
                'comp': move.partner_id.commercial_company_name or 'N/A',
                'partner': move.partner_id.name or 'N/A',
                'reference': move.reference or 'N/A',
                'origin': move.origin or move.picking_id.origin or move.picking_id.name or 'N/A'  # Додаємо поле початкового документа
            })
            if partner.commercial_company_name:  # Перевірка, чи є назва компанії
                companies.add(partner.commercial_company_name)
            if responsible_user:
                responsible_users.add(responsible_user)
        # Сортуємо компанії
        sorted_companies = sorted(list(companies))  # Сортування алфавітно
        # Сортуємо імена для звіту
        sorted_responsible_users = sorted(list(responsible_users)) # Сортування алфавітно

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
                    'date': group[0]['date'] or 'N/A',
                    'comp': group[0]['comp'] or 'N/A',
                    'partner': group[0]['partner'] or 'N/A',
                    'pichA': product_quantities.get("Бук сорт A", 0) or 0,
                    'pichB': product_quantities.get("Бук сорт B", 0) or 0,
                    'pichC': product_quantities.get("Бук сорт C", 0) or 0,
                    'pichD': product_quantities.get("Бук сорт D", 0) or 0,
                    'reference': reference,
                    'origin': group[0]['origin'] or 'N/A',  # Додаємо поле початкового документа
                    'quantity': sum(product_quantities.values())
                }
                # Додаємо відсоткове співвідношення
                total_quantity = processed_item['quantity'] or 1  # Уникаємо ділення на 0

                processed_item.update({
                    'pichA%': round((processed_item['pichA'] / total_quantity) * 100, 2),
                    'pichB%': round((processed_item['pichB'] / total_quantity) * 100, 2),
                    'pichC%': round((processed_item['pichC'] / total_quantity) * 100, 2),
                    'pichD%': round((processed_item['pichD'] / total_quantity) * 100, 2),
                })
                # Перевіряємо, чи всі значення pichA, pichB, pichC, pichD дорівнюють 0
                if not (processed_item['pichA'] == 0 and
                        processed_item['pichB'] == 0 and
                        processed_item['pichC'] == 0 and
                        processed_item['pichD'] == 0):
                    processed_report_data.append(processed_item)

            # Формування об'єкту статистики
            summary = {
                'total_quantities': dict(total_quantities) or {
                    'pichA': 0,
                    'pichB': 0,
                    'pichC': 0,
                    'pichD': 0,
                },
                'total_overall_quantity': round(total_overall_quantity or 0, 3) or 0
            }

            # Перевіряємо та присвоюємо 0, якщо значення відсутнє або None
            for key in ['pichA', 'pichB', 'pichC', 'pichD']:
                summary['total_quantities'][key] = summary['total_quantities'].get(key, 0)

            # Додаємо відсоткове співвідношення
            total_quantity = summary['total_overall_quantity'] or 1  # Уникаємо ділення на 0

            summary['total_percentages'] = {
                'pichA%': round((summary['total_quantities'].get('pichA', 0) / total_quantity) * 100, 2),
                'pichB%': round((summary['total_quantities'].get('pichB', 0) / total_quantity) * 100, 2),
                'pichC%': round((summary['total_quantities'].get('pichC', 0) / total_quantity) * 100, 2),
                'pichD%': round((summary['total_quantities'].get('pichD', 0) / total_quantity) * 100, 2),
            }

            return processed_report_data, summary

        # Виклик функції
        processed_report_data, summary = process_report_data(report_data_grouped)
        # print(sorted_companies)

        # Приклад використання
        #     print("Оброблені дані:", processed_report_data)
        #     print("\nЗагальна статистика:")
        #     print("Кількість по кожному продукту:", summary['total_quantities'])
        #     print("Загальна кількість:", summary['total_overall_quantity'])

        return {
            'doc_ids': docids,
            'doc_model': 'raw.materials.report.wizard',
            'docs': report,
            'data': [processed_report_data, summary, sorted_companies,sorted_responsible_users],
            'start_date': start_date,
            'end_date': end_date,
        }


class RawMaterialsReportWizard(models.TransientModel):
    _name = 'raw.materials.report.wizard'
    _description = 'Майстер звіту про сировину'

    start_date = fields.Date(string='Дата з', required=True)
    end_date = fields.Date(string='Дата до', required=True)

    def action_gen_report_pdf(self):
        report_action = self.env.ref('raw_materials_report.raw_materials_report_action_pdf').report_action(self)
        return report_action

    def action_gen_report_html(self):
        report_action = self.env.ref('raw_materials_report.raw_materials_report_action_html').report_action(self)
        return report_action
    