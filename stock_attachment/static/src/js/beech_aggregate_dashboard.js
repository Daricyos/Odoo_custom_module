/**@odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "./kpi_card";
import { Camera } from "./camera";

const actionRegistry = registry.category("actions");
const { onWillStart } = owl

class CrmDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm'); // ORM для взаимодействия с сервером

        this.state = {
            kpiData: [
                { name: "Залишок на складі", value: 0 },
                { name: "Прихід сьогодні", value: 0, percentage: 0, unit: "машин" },
                { name: "У виробництві", value: 0, percentage: 0, unit: "партій" },
//                { name: "Ефективність", value: 78.5, percentage: 2.1, unit: "%" },
            ],
            cameraData: [
                { name: "Камера №6", volume: " м³", loadingStatus: "Завантаження %" },
                { name: "Камера №7", volume: " м³", loadingStatus: "Завантаження %" },
                { name: "Камера №8", volume: " м³", loadingStatus: "Завантаження %" },
                { name: "Камера №1", volume: " м³", loadingStatus: "Завантаження %" },
                { name: "Всього в камерах", volume: " м³", loadingStatus: " активні камери" },
            ],
            tableData: [{
                sort: 0, quantity: 0, incomingToday: 0, inProduction: 0
            }],
        };

        onWillStart(async ()=>{
            await this._fetchData()
        });
    }

    // Закомментированный метод для получения данных с сервера
    async _fetchData() {
        const currentBalances = await this.orm.readGroup(
            'product.product',
            [['name', 'ilike', 'Бук сорт']],
            ['qty_available:sum'], []
        )

        //Прихід сьогодні

        const wareHouse = await this.orm.searchRead("stock.warehouse",
            [],
            ['name','id'], []
        );
        const wareHouseId = wareHouse.map(warehouse => warehouse.id);


        const pickingType = await this.orm.searchRead("stock.picking.type",
            [
                ['warehouse_id', '=', wareHouseId],
                ['code', '=', 'incoming'],
            ],
            ['name','id'],
        );


        const pickingTypeId = pickingType.map(picking => picking.id);

        let startOfDay = new Date();
        startOfDay.setHours(0, 0, 0, 0);
        let endOfDay = new Date();
        endOfDay.setHours(23, 59, 59, 999);


        let domain = [
            ['state', 'in', ['done']],
            ['product_id', 'ilike', 'Бук сорт'],
            ['picking_type_id', '=', pickingTypeId],
            ['date_done', '>=', startOfDay.toISOString()],
            ['date_done', '<=', endOfDay.toISOString()]
        ]

        const recordCount = await this.orm.search('stock.picking', domain);
        const data = await this.orm.readGroup('stock.picking', domain, ['product_quantity_t:sum'],[])

        //У виробництві

        let domain_production = [
            ['state', '=', 'progress'],
        ]


        const productions = await this.orm.searchRead(
            'mrp.production',
            domain_production,
            ['name']
        );

        const productionIds = productions.map(p => p.id);

        const domain_moves = [
            ['raw_material_production_id', 'in', productionIds],
            ['product_id.display_name', 'ilike', 'Бук сорт'],
        ];

        const stockMoves = await this.orm.searchRead(
            'stock.move',
            domain_moves,
            ['raw_material_production_id', 'quantity']
        );

        const totalQuantity = stockMoves.reduce((sum, move) => sum + (move.quantity || 0), 0);
        const totalCount = stockMoves.length;

        const productionQty = currentBalances[0].qty_available
        const comingToday = data[0].product_quantity_t
        const recordCountToday = recordCount.length
        const inProduction = totalQuantity
        const totalCountProduction = totalCount


        // Добавь свой код сюда

        const bukProducts = await this.orm.searchRead(
            'product.product',
            [['name', 'ilike', 'Бук сорт']],
            ['id', 'name', 'qty_available']
        );

        const tableData = [];
        for (const product of bukProducts) {
            // Для "Прихід сьогодні" по конкретному продукту
            let productDomain = [
                ['state', 'in', ['done']],
                ['product_id', '=', product.id],
                ['picking_type_id', 'in', pickingTypeId],
                ['date_done', '>=', startOfDay.toISOString()],
                ['date_done', '<=', endOfDay.toISOString()]
            ];
            const productIncomingGroup = await this.orm.readGroup('stock.picking', productDomain, ['product_quantity_t:sum'], []);
            const productIncoming = (productIncomingGroup && productIncomingGroup.length > 0) ? productIncomingGroup[0].product_quantity_t : 0;

            // Для "У виробництві" по конкретному продукту
            let productionDomain = [
                ['raw_material_production_id', 'in', productionIds],
                ['product_id', '=', product.id],
            ];
            const stockMovesForProduct = await this.orm.searchRead('stock.move', productionDomain, ['quantity']);
            const inProductionQty = stockMovesForProduct.reduce((sum, move) => sum + (move.quantity || 0), 0);

            tableData.push({
                sort: product.name,            // Название сорта
                quantity: product.qty_available, // Залишок на складі
                incomingToday: productIncoming,  // Прихід сьогодні
                inProduction: inProductionQty,   // У виробництві
            });
        }

        this.state.tableData = tableData;




        // тут конец твоего кода



        this.state.kpiData[0].value = productionQty;
        this.state.kpiData[1].value = comingToday;
        this.state.kpiData[2].value = inProduction;
        this.state.kpiData[1].percentage = recordCountToday;
        this.state.kpiData[2].percentage = totalCountProduction;

    }
}

// Подключаем шаблон и компоненты
CrmDashboard.template = "stock_attachment.CrmDashboard";
CrmDashboard.components = { KpiCard, Camera };

// Регистрируем действие в Odoo
actionRegistry.add("stock_attachment.beech_aggregate_dashboard_tag", CrmDashboard);
