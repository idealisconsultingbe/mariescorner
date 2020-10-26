# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductionSalesLot(models.Model):
    _inherit = 'stock.production.sales.lot'

    delivery_date = fields.Date(string='Planned Delivery Date', compute='_compute_delivery_date', store=True, help='Planned date provided by production team')

    @api.depends('production_ids.delivery_date')
    def _compute_delivery_date(self):
        for sales_lot in self:
            dates_list = [production.delivery_date for production in sales_lot.production_ids]
            if dates_list:
                sales_lot.delivery_date = max(dates_list)
            else:
                sales_lot.delivery_date = False
