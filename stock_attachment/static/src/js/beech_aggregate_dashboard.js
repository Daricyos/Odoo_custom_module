/**@odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "./kpi_card";
import { Camera } from "./camera";

const actionRegistry = registry.category("actions");

class CrmDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm'); // ORM для взаимодействия с сервером

        this.state = {
            kpiData: [
                { name: "Залишок на складі", value: 2345, percentage: 20, unit: "%" },
                { name: "Прихід сьогодні", value: 245, percentage: 8, unit: "машин" },
                { name: "У виробництві", value: 180, percentage: 5, unit: "партій" },
                { name: "Ефективність", value: 78.5, percentage: 2.1, unit: "%" },
            ],
            cameraData: [
                { name: "Камера №6", volume: "85 м³", loadingStatus: "Завантаження 85%" },
                { name: "Камера №7", volume: "90 м³", loadingStatus: "Завантаження 75%" },
                { name: "Камера №8", volume: "80 м³", loadingStatus: "Завантаження 65%" },
                { name: "Камера №1", volume: "100 м³", loadingStatus: "Завантаження 50%" },
                { name: "Всього в камерах", volume: "340 м³", loadingStatus: "4 активні камери" },
            ],
        };

        // Закомментированный вызов для получения данных с бэкенда
        /*
        this._fetchData();
        */
    }

    // Закомментированный метод для получения данных с сервера
    /*
    async _fetchData() {
        try {
            const result = await this.orm.call("crm.lead", "get_tiles_data", [], {});
            this.state.kpiData = result.kpiData || []; // Предполагаемая структура ответа
            this.state.cameraData = result.cameraData || []; // Предполагаемая структура ответа
            this.render(); // Обновление интерфейса
        } catch (error) {
            console.error("Ошибка при вызове get_tiles_data:", error);
        }
    }
    */
}

// Подключаем шаблон и компоненты
CrmDashboard.template = "stock_attachment.CrmDashboard";
CrmDashboard.components = { KpiCard, Camera };

// Регистрируем действие в Odoo
actionRegistry.add("stock_attachment.beech_aggregate_dashboard_tag", CrmDashboard);

export default CrmDashboard;
