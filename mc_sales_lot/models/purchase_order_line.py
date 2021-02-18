# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Manufacturing Number', readonly=True, copy=False)

    def _prepare_account_move_line(self, move):
        """ add manufacturing numbers to supplier invoice lines values """
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        if res and self.sales_lot_id:
            res['sales_lot_ids'] = [(4, self.sales_lot_id.id, 0)]
        return res
