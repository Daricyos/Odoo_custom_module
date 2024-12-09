/**@odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

const actionRegistry = registry.category("actions");

class CrmDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm'); // ORM для взаимодействия с сервером
        this._fetch_data();          // Вызов функции получения данных
    }

    _fetch_data() {
        this.orm.call("crm.lead", "get_tiles_data", [], {}).then((result) => {
            document.getElementById('my_lead').innerHTML = `<span>${result.total_leads}</span>`;
            document.getElementById('my_opportunity').innerHTML = `<span>${result.total_opportunity}</span>`;
            document.getElementById('revenue').innerHTML = `<span>${result.currency}${result.expected_revenue}</span>`;
        });
    }
}

CrmDashboard.template = "stock_attachment.CrmDashboard"; // Указываем шаблон
actionRegistry.add("beech_aggregate_dashboard_tag", CrmDashboard); // Регистрация действия
