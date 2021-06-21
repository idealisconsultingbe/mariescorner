# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    sales_lot_ids = fields.Many2many('stock.production.sales.lot', 'sales_lot_stock_lot_rel', 'stock_lot_id', 'sales_lot_id', string='Manufacturing Numbers', readonly=True)