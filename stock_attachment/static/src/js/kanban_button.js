/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { useService } from "@web/core/utils/hooks";

export class CustomKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    async onReceivingWoodClick() {
        const action = {
            name: "Receiving Wood",
            type: "ir.actions.act_window",
            res_model: "receiving.wood",
            views: [[false, "form"]],
        };
        this.actionService.doAction(action);
    }
}

registry.category("views").add("custom_kanban", {
    ...kanbanView,
    Controller: CustomKanbanController,
    buttonTemplate: "stock_attachment.KanbanView.Buttons",
});
