# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    short_name = fields.Text(string='Description', store=True, compute='_compute_short_name')

    @api.depends('sales_lot_ids', 'sales_lot_ids.short_name')
    def _compute_short_name(self):
        for lot in self:
            lot.short_name = ''
            if lot.sales_lot_ids:
                lot.short_name = lot.sales_lot_ids.sorted('id')[0].short_name
