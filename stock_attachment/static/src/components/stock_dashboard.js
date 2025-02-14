/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCardStock } from "./kpi_card/kpi_card_stock"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, useState } = owl
//import { getColor } from "@web/views/graph/colors"

export class StockAttachmentDashboard extends Component {
    //Коефіцієнти переробки
    getTopProducts(){
        this.state.topProducts = {

        }
    }
    //Вироблено чураку
    getChurakuProduced(){
        this.state.churakuProduced = {}
    }

    // Прихід деревини по сортах
    async getArrivalWoodGrade(){
//        const data = await this.orm.readGroup(
//            "stock.picking",
//            [],
//            ['picking_type_id', 'date_done'], ['picking_type_id'])
//        console.log(data)
        this.state.arrivalWoodGrade = {
            data: {
//                labels: data.map(d => d.product_id[1]),
//                  datasets: [
//                  {
//                    label: 'Total',
//                    data: data.map(d => d.product_id_count[1]),
//                    hoverOffset: 4
//                  },{
//                    label: 'My Second Dataset',
//                    data: [100, 70, 150],
//                    hoverOffset: 4
//                  }]
            }
        }
    }


    setup(){
        this.state = useState({
            quotations:{
                value:10,
                percentage:6,
            },
            period:90,
        })
        this.orm = useService("orm")
        this.actionService = useService("action")

        onWillStart(async ()=>{
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js")
            this.getDates()
            await this.qetQuotations()
            await this.qetManufactured()

            this.getTopProducts()
            this.getChurakuProduced()
            await this.getArrivalWoodGrade()
        })
    }

    async onChangePeriod(){
        this.getDates()
        await this.qetQuotations()
        await this.qetManufactured()
    }

    getDates(){
        this.state.current_date = moment().subtract(this.state.period, 'days').format('L')
        this.state.previous_date = moment().subtract(this.state.period * 2, 'days').format('L')
    }

    async qetQuotations(){
        const wareHouse = await this.orm.searchRead("stock.warehouse",
            [],
            ['id']
        );

        const wareHouseId = wareHouse.map(warehouse => warehouse.id);

        this.state.wareHouseId = wareHouseId;

        const pickingType = await this.orm.searchRead("stock.picking.type",
            [
                ['warehouse_id', '=', wareHouseId],
                ['code', '=', 'incoming'],
            ],
            ['id']
        );

        const pickingTypeId = pickingType.map(picking => picking.id);

        this.state.pickingTypeId = pickingTypeId;

        let domain = [['state', 'in', ['done']], ['picking_type_id', '=', pickingTypeId]]
        if (this.state.period > 0){
            domain.push(
                ['date_done', '>', this.state.current_date]
            )
        }

        const data = await this.orm.readGroup('stock.picking', domain, ['product_quantity_t:sum'],[])

        this.state.quotations.value = `${data[0].product_quantity_t}m³`

        // previous period

        let prev_domain = [['state', 'in', ['done']], ['picking_type_id', '=', pickingTypeId]]
        if (this.state.period > 0){
            prev_domain.push(
                ['date_done', '>', this.state.previous_date], ['date_done', '<=', this.state.current_date]
            )
        }
        const prev_data = await this.orm.readGroup('stock.picking', domain, ['product_quantity_t:sum'],[])
        const percentage = (
            (
                data[0].product_quantity_t - prev_data[0].product_quantity_t
            ) / prev_data[0].product_quantity_t
        ) * 100

        this.state.quotations.percentage = percentage.toFixed(2)
    }

    async qetManufactured(){
        const wareChuraku = await this.orm.searchRead("product.product",
            [['name', 'ilike', 'Чурак']],
            ['id']
        );

        const wareChurakuId = wareChuraku.map(product => product.id);


        let domain = [['state', 'in', ['done']], ['product_id', '=', wareChurakuId]]
        if (this.state.period > 0){
            domain.push(
                ['date_finished', '>', this.state.current_date]
            )
        }
        const current_product = await this.orm.readGroup('mrp.production', domain, ["product_qty:sum"],[])

        // previous period

        let prev_domain = [['state', 'in', ['done']], ['product_id', '=', wareChurakuId]]
        if (this.state.period > 0){
            prev_domain.push(
                ['date_finished', '>', this.state.previous_date], ['date_finished', '<=', this.state.current_date]
            )
        }

        const prev_product_qty = await this.orm.readGroup('mrp.production', prev_domain, ["product_qty:sum"],[])
        const product_qty_percentage = (
            (current_product[0].product_qty - prev_product_qty[0].product_qty) / prev_product_qty[0].product_qty
        ) * 100




        this.state.orders = {
            product_qty: `${current_product[0].product_qty}m³`,
            product_qty_percentage: product_qty_percentage.toFixed(2),
        }
    }

    viewQuotations(){
        let domain = [['state', 'in', ['done']], ['picking_type_id', '=', this.state.pickingTypeId]]
        if (this.state.period > 0){
            domain.push(
                ['date_done', '>', this.state.current_date]
            )
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "stock.picking",
            domain,
            views: [
                [false, "list"],
                [false, "form"],
            ]
        })
    }
}

StockAttachmentDashboard.template = "stock_attachment.StockAttachmentDashboard"
StockAttachmentDashboard.components = { KpiCardStock, ChartRenderer }

registry.category("actions").add("stock_attachment.dashboard_stock", StockAttachmentDashboard)