# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_compare


class CreateVendorBill(models.TransientModel):
    _name = 'create.vendor.account.move'
    _description = 'Create Vendor Bills for Inter-Company Transactions'

    invoicing_type = fields.Selection([('without_intercompany_lines', 'Bills without inter-company lines'), ('with_intercompany_lines', 'Bills with inter-company lines')], string='Inter-Company Invoicing Type', default='without_intercompany_lines', required=True, help='Choose whether inter-company lines should be invoiced or not')
    billing_message = fields.Char(string='Invoicing Type Message', compute='_compute_billing_message')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    block_billing = fields.Boolean(string='Block Billing', compute='_compute_billing_message', help='Used in UI to prevent billing if there are no invoiceable lines')

    @api.depends('purchase_order_id')
    def _compute_billing_message(self):
        """
        Compute wizard message to inform user whether there are invoiceable lines linked to an inter-company transaction or not
        """
        for wiz in self:
            msg = ''
            if wiz.purchase_order_id:
                wiz.block_billing = False
                invoiceable_quantity = sum([order_line.qty_received - order_line.qty_invoiced for order_line in wiz.purchase_order_id.order_line])
                if float_compare(invoiceable_quantity, 0.0, precision_digits=self.env['decimal.precision'].precision_get('Product Unit of Measure')) <= 0:
                    wiz.block_billing = True
                    msg = _('There is no invoiceable line for this purchase order.')
                else:
                    intercompany_sale_order_lines = self.sudo().env['sale.order.line'].search([('inter_company_po_line_id', 'in', wiz.purchase_order_id.order_line.ids)])
                    if not intercompany_sale_order_lines:
                        msg = _('No purchase order line is part of an inter-company transaction.')
                    elif all([line in intercompany_sale_order_lines.mapped('inter_company_po_line_id') for line in wiz.purchase_order_id.order_line]):
                        msg = _('All purchase order lines are linked to an inter-company transaction.')
                    else:
                        msg = _('Some purchase order lines are linked to an inter-company transaction.')
            wiz.billing_message = msg

    def action_create_vendor_bill(self):
        """
        Call 'Create Invoice' button method
        To prevent wizard to be displayed again, there is context information on button
        """
        self.ensure_one()
        if self.purchase_order_id:
            return self.purchase_order_id.action_view_invoice()

