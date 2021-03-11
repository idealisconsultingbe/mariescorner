# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_status = fields.Selection(selection_add=[('partial', 'Partially Invoiced')])

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoice_status(self):
        """
        Overridden method

        Add partial invoice status if there are no more quantities to invoice but
        at least one downpayment is not already paid
        """
        super(SaleOrder, self)._get_invoice_status()
        for order in self:
            if order.invoice_status in ['no', 'to invoice']:
                continue
            if any(line.invoice_status == 'partial' for line in order.order_line):
                order.invoice_status = 'partial'
