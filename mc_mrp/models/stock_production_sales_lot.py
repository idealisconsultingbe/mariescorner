# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductionSalesLot(models.Model):
    _inherit = 'stock.production.sales.lot'

    delivery_date = fields.Date(string='Planned Delivery Date', compute='_compute_delivery_date', store=True, help='Estimated delivery date provided by production team')
    short_name = fields.Text(string='Description', related='origin_sale_order_line_id.short_name')
    sale_comment = fields.Text(string='Sale Comment', related='origin_sale_order_line_id.comment')

    @api.depends('production_ids.delivery_date', 'ext_delivery_date')
    def _compute_delivery_date(self):
        """
        Compute delivery date from subcontractor if supplier type is external, else select the most distant date from production orders
        Compute of stored fields is always in sudo mode by default
        """
        for sales_lot in self:
            if sales_lot.supplier_type == 'external':
                sales_lot.delivery_date = sales_lot.ext_delivery_date
            else:
                dates_list = [production.delivery_date for production in sales_lot.production_ids]
                if dates_list:
                    sales_lot.delivery_date = max(dates_list)
                else:
                    sales_lot.delivery_date = False
