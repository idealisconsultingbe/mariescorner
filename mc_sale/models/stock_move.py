# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_purchase_line_id(self):
        """
        Go through the stock move chain in a up bottom way.
        Return the first purchase order line found.
        """
        current_move = self
        po_line = self.env['purchase.order.line']
        while current_move:
            if current_move.created_purchase_line_id:
                po_line = current_move.created_purchase_line_id
                current_move = self.env['stock.move']
            elif current_move.move_orig_ids:
                current_move = current_move.move_orig_ids[0]
            else:
                current_move = self.env['stock.move']
        return po_line
