from odoo import http
from odoo.http import request

class AggregatedForemanReportController(http.Controller):
    @http.route('/aggregated_foreman_report', type='http', auth='user', website=True)
    def aggregated_foreman_report(self, **kwargs):
        return request.render('raw_materials_report.aggregated_foreman_report_form_template')
