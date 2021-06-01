# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Manufacturing Number', readonly=True, copy=False)
    sales_lot_activated = fields.Boolean(string='Sales Lot Activated', related='product_id.sales_lot_activated')
    date_msc_planned = fields.Datetime(string='Date planned')

    @api.onchange('date_msc_planned')
    def _onchange_date_planned(self):
        if self.date_msc_planned:
            self.date_planned = self.date_msc_planned

    def _find_candidate(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        # if this is defined, this is a dropshipping line, so no
        # this is to correctly map delivered quantities to the so lines
        lines = self.filtered(lambda po_line: po_line.sales_lot_id.id == values['sales_lot_id']) if values.get('sales_lot_id') else self
        return super(PurchaseOrderLine, lines)._find_candidate(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)

    def _prepare_account_move_line(self, move):
        """ add manufacturing numbers to supplier invoice lines values """
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        if res and self.sales_lot_id:
            res['sales_lot_ids'] = [(4, self.sales_lot_id.id, 0)]
        return res

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for re in res:
            if self.product_id.sales_lot_activated and self.sales_lot_id.id:
                re['sales_lot_id'] = self.sales_lot_id.id
        return res

