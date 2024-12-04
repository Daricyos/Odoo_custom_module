from odoo import models, fields, api



class AggregatedForemanReport(models.Model):
    _name = 'aggregated.foreman.report'
    _description = 'Агрегована форма бригадира'

    # Поля для збереження даних
    name = fields.Char(string="Назва звіту", default="Агрегована форма бригадира")
    date = fields.Date(string="Дата звіту", default=fields.Date.context_today)
    total_volume = fields.Float(string="Загальний об'єм (м³)")
    
    # Поля для збереження об'єму по кожному сорту
    sort_a_volume = fields.Float(string="Об'єм сорту A (м³)")
    sort_b_volume = fields.Float(string="Об'єм сорту B (м³)")
    sort_c_volume = fields.Float(string="Об'єм сорту C (м³)")
    sort_d_volume = fields.Float(string="Об'єм сорту D (м³)")

    # Поля для збереження відсотків
    sort_a_percent = fields.Float(string="Відсоток сорту A")
    sort_b_percent = fields.Float(string="Відсоток сорту B")
    sort_c_percent = fields.Float(string="Відсоток сорту C")
    sort_d_percent = fields.Float(string="Відсоток сорту D")

    # Поле для додаткових коментарів
    notes = fields.Text(string="Коментарі")

    # Обчислюване поле для загального відсотка
    @api.depends('sort_a_volume', 'sort_b_volume', 'sort_c_volume', 'sort_d_volume', 'total_volume')
    def _compute_percentages(self):
        for record in self:
            if record.total_volume:
                record.sort_a_percent = (record.sort_a_volume / record.total_volume) * 100 if record.sort_a_volume else 0.0
                record.sort_b_percent = (record.sort_b_volume / record.total_volume) * 100 if record.sort_b_volume else 0.0
                record.sort_c_percent = (record.sort_c_volume / record.total_volume) * 100 if record.sort_c_volume else 0.0
                record.sort_d_percent = (record.sort_d_volume / record.total_volume) * 100 if record.sort_d_volume else 0.0
            else:
                record.sort_a_percent = record.sort_b_percent = record.sort_c_percent = record.sort_d_percent = 0.0
