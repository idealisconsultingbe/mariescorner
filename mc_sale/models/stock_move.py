# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', compute='_compute_sales_lot_id', string='Sales Lot', store=True)

    @api.depends('sale_line_id.sales_lot_id')
    def _compute_sales_lot_id(self):
        for move in self:
            if move.sale_line_id:
                move.sales_lot_id = move.sale_line_id.sales_lot_id
            elif move.move_dest_ids:
                if len(move.move_dest_ids.mapped('sales_lot_id')) == 1 and all(move.sales_lot_id for move in move.move_dest_ids):
                    move.sales_lot_id = move.move_dest_ids[0].sales_lot_id

