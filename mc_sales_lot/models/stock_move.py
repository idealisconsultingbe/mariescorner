# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Manufacturing Number')

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None, lot_name=None):
        """ Overridden method
            Add lot name to move lines
        """
        res = super(StockMove, self)._prepare_move_line_vals(quantity, reserved_quant)
        if lot_name:
            res['lot_name'] = lot_name
        return res

    def _merge_moves(self, merge_into=False):
        """
        Override the standard method -> it will prevent move using manufacturing number to be merged.
        """
        moves_using_sales_lot = self.filtered(lambda m: m.product_id.sales_lot_activated)
        merged_moves = super(StockMove, self - moves_using_sales_lot)._merge_moves(merge_into)
        return (merged_moves | moves_using_sales_lot)

    def _prepare_procurement_values(self):
        """
        Override standard method -> add the manufacturing number into the procurement.
        :return:
        """
        values = super(StockMove, self)._prepare_procurement_values()
        if self.product_id.sales_lot_activated and self.sales_lot_id:
            values['sales_lot_id'] = self.sales_lot_id.id
        return values
