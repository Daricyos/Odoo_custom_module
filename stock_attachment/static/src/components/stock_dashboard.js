/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCardStock } from "./kpi_card/kpi_card_stock"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, useState } = owl

export class StockAttachmentDashboard extends Component {
    //Вироблено чураку
    async getChurakuProduced(){
        let domain = [['state', 'in', ['done']], ['product_id', '=', this.state.wareChurakuId]]
        if (this.state.period > 0){
            domain.push(
                ['date_finished', '>', this.state.current_date]
            )
        }

        const data = await this.orm.readGroup(
            "mrp.production",
            domain,
            ['product_id', 'product_qty'],
            ['product_id'],
        );

        this.state.churakuProduced = {
            data: {
                labels: data.map(d => d.product_id[1]),
                  datasets: [
                  {
                    label: 'Total',
                    data: data.map(d => d.product_qty),
                    hoverOffset: 4,
                  }]
            }
        }
    }

    // Прихід деревини по сортах
    async getArrivalWoodGrade(){
        let domain = [['picking_id.state', 'in', ['done']], ['picking_id.picking_type_id', '=', this.state.pickingTypeId]]
        if (this.state.period > 0){
            domain.push(
                ['picking_id.date_done', '>', this.state.current_date]
            )
        }

        const data = await this.orm.readGroup(
            "stock.move",
            domain,
            ['product_id', 'product_uom_qty'],
            ['product_id'],
        );

        this.state.arrivalWoodGrade = {
            data: {
                labels: data.map(d => d.product_id[1]),
                  datasets: [
                  {
                    label: 'Total',
                    data: data.map(d => d.product_uom_qty),
                    hoverOffset: 4,
                  }]
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
            await this.getRecyclingRates()

            await this.getChurakuProduced()
            await this.getArrivalWoodGrade()
        })
    }

    async onChangePeriod(){
        this.getDates()
        await this.qetQuotations()
        await this.qetManufactured()
        await this.getRecyclingRates()
    }

    getDates(){
        this.state.current_date = moment().subtract(this.state.period, 'days').format('L')
        this.state.previous_date = moment().subtract(this.state.period * 2, 'days').format('L')
    }

    // Прихід деревини по сортах
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

    //Вироблено чураку
    async qetManufactured(){
        const wareChuraku = await this.orm.searchRead("product.product",
            [['name', 'ilike', 'Чурак']],
            ['id']
        );

        const wareChurakuId = wareChuraku.map(product => product.id);

        this.state.wareChurakuId = wareChurakuId;


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

    //Коефіцієнти переробки
    async getRecyclingRates(){
        let domain = [['state', 'in', ['done']]]
        if (this.state.period > 0){
            domain.push(
                ['date_finished', '>', this.state.current_date]
            )
        }
        const recycling_rates = await this.orm.readGroup('mrp.production', domain, ["processing_coefficient:sum"],[])

        // previous period

        let prev_domain = [['state', 'in', ['done']]]
        if (this.state.period > 0){
            prev_domain.push(
                ['date_finished', '>', this.state.previous_date], ['date_finished', '<=', this.state.current_date]
            )
        }

        const prev_recycling_rates = await this.orm.readGroup('mrp.production', prev_domain, ["processing_coefficient:sum"],[])
        const recycling_rates_percentage = (
            (recycling_rates[0].processing_coefficient - prev_recycling_rates[0].processing_coefficient) / prev_recycling_rates[0].processing_coefficient
        ) * 100

        //table view
//        const recyclingRatesSettings = await this.orm.readGroup(
//            'res.config.settings',
//            [],
//            ['recycling_rates']
//        );
//        console.log('recyclingRatesSettings', recyclingRatesSettings)

        const productionRecords = await this.orm.readGroup(
            'mrp.production',
            domain,
            ['product_id', 'product_qty', 'processing_coefficient', 'total_raw_material_qty'], ['product_id']
        );

        console.log('productionRecords', productionRecords)
        this.state.productionRecords = productionRecords;


        this.state.rates = {
            recycling_rates: recycling_rates[0].processing_coefficient,
            recycling_rates_percentage: recycling_rates_percentage.toFixed(2),
//            product_id: record.product_id[1],
//            product_qty: record.product_qty,
//            processing_coefficient: record.processing_coefficient,
        }
    }


    // Прихід деревини по сортах view
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

    //Вироблено чураку
    viewChurakuProduced(){
        let domain = [['state', 'in', ['done']], ['product_id', '=', this.state.wareChurakuId]]
        if (this.state.period > 0){
            domain.push(
                ['date_finished', '>', this.state.current_date]
            )
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "ChurakuProduced",
            res_model: "mrp.production",
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