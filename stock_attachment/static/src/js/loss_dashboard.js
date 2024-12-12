/**@odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Camera } from "./camera";
import {BatchDetailsTable} from "./batch_details_table";

const actionRegistry = registry.category("actions");

class LossDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm'); // ORM для взаимодействия с сервером

        this.state = {
            cameraData: [
                { name: "Загальний вихід шпону", volume: "65.8%", loadingStatus: "+2.1% від середнього" },
                { name: "Відходи", volume: "19.4%", loadingStatus: "-1.2% від середнього" },
                { name: "Карандаші", volume: "14.8%", loadingStatus: "В межах норми" },
                { name: "Брак", volume: "3.2%", loadingStatus: "Вище норми на 0.7%" }
            ],
            batches: [
                { name: "Партія 1", inputVolume: 100, outputPlywood: 65, pencils: 15, waste: 20, efficiency: 65 },
                { name: "Партія 2", inputVolume: 100, outputPlywood: 70, pencils: 12, waste: 18, efficiency: 70 },
                { name: "Партія 3", inputVolume: 100, outputPlywood: 62, pencils: 18, waste: 20, efficiency: 62 }
            ],
        };
    }
}
// Подключаем шаблон и компоненты
LossDashboard.template = "stock_attachment.LossDashboard";
LossDashboard.components = { Camera, BatchDetailsTable };

// Регистрируем действие в Odoo
actionRegistry.add("stock_attachment.loss_dashboard_tag", LossDashboard);
