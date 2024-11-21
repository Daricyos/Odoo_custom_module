from odoo import models, fields


class RawMaterialsReportWizard(models.TransientModel):
    _name = 'raw.materials.report.wizard'

    def action_gen_report(self):
        report_action = self.env.ref('raw_materials_report.raw_materials_report_action').report_action(self)
        return report_action
    # date_from = fields.Date('Дата з')
    # date_to = fields.Date('Дата до')