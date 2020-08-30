# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', compute='_compute_sales_lot_id', string='Sales Lot', store=True)

    @api.depends('sale_line_id.sales_lot_id', 'move_dest_ids.sales_lot_id')
    def _compute_sales_lot_id(self):
        """ Compute M2o relation to Stock Production Sales Lot.
            There are 2 possible cases:
                - a stock move may have a relationship to a sale order line with Sales Lot, then retrieve it
                - a stock move may have in its next stock moves a Sales Lot and then retrieve it
        """
        for move in self:
            if move.sale_line_id:
                move.sales_lot_id = move.sale_line_id.sales_lot_id
            elif move.move_dest_ids:
                # if all stock moves have the same Sales Lot then add it to values
                if len(move.move_dest_ids.mapped('sales_lot_id')) == 1 and all(move.sales_lot_id for move in move.move_dest_ids):
                    move.sales_lot_id = move.move_dest_ids[0].sales_lot_id

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None, lot_name=None):
        """ Overridden method
            Add lot name to move lines
        """
        res = super(StockMove, self)._prepare_move_line_vals(quantity, reserved_quant)
        if lot_name:
            res['lot_name'] = lot_name
        return res