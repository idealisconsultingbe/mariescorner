# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    invoice_status = fields.Selection(selection_add=[('partial', 'Partially Invoiced')])

    @api.depends('state',
                 'is_downpayment',
                 'product_uom_qty',
                 'qty_delivered',
                 'qty_to_invoice',
                 'qty_invoiced',
                 'untaxed_amount_to_invoice',
                 'untaxed_amount_invoiced')
    def _compute_invoice_status(self):
        """
        Overridden method
        An invoiced downpayment line is 'fully invoiced' if paid, else 'partially invoiced'
        """
        super(SaleOrderLine, self)._compute_invoice_status()
        for line in self:
            if line.is_downpayment and line.untaxed_amount_to_invoice == 0:
                line.invoice_status = 'invoiced'
            elif line.is_downpayment and line.untaxed_amount_to_invoice == -line.untaxed_amount_invoiced:
                line.invoice_status = 'partial'
