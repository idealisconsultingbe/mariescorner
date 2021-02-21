# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductionSalesLot(models.Model):
    _inherit = 'stock.production.sales.lot'

    short_name = fields.Text(string='Description', related='origin_sale_order_line_id.short_name')
    delivery_date = fields.Date(string='Planned Delivery Date', compute='_compute_production_dates', store=True, help='Estimated delivery date provided by production team or subcontractor')
    fabric_date = fields.Date(string='Fabric Date', compute='_compute_production_dates', store=True, help='Fabric date provided by production team')
    sale_comment = fields.Text(string='Sale Comment', related='origin_sale_order_line_id.comment')

    @api.depends('production_ids.delivery_date', 'ext_delivery_date', 'production_ids.fabric_date')
    def _compute_production_dates(self):
        """
        Compute delivery date from subcontractor if supplier type is external, else select the most distant date from production orders
        Compute fabric date, select the earliest date from all production orders fabric dates

        Compute of stored fields is always in sudo mode by default
        """
        for sales_lot in self:
            if sales_lot.supplier_type == 'external':
                sales_lot.fabric_date = False
                sales_lot.delivery_date = sales_lot.ext_delivery_date
            else:
                delivery_dates_list = [production.delivery_date for production in sales_lot.production_ids]
                fabric_dates_list = [production.fabric_date for production in sales_lot.production_ids]
                if delivery_dates_list:
                    sales_lot.delivery_date = max(delivery_dates_list)
                else:
                    sales_lot.delivery_date = False
                if fabric_dates_list:
                    sales_lot.fabric_date = min(fabric_dates_list)
                else:
                    sales_lot.fabric_date = False
