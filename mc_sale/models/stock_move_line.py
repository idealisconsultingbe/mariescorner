# -*- coding: utf-8 -*-
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', related='move_id.sales_lot_id', string='Sales Lot')
