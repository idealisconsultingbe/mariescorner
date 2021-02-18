# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CreateVendorBill(models.TransientModel):
    _name = 'create.vendor.account.move'
    _description = 'Create Vendor Bills for Inter-Company Transactions'

    invoicing_type = fields.Selection([('without_intercompany_lines', 'Bills without inter-company lines'), ('with_intercompany_lines', 'Bills with inter-company lines')], string='Inter-Company Invoicing Type', default='without_intercompany_lines', required=True, help='Choose whether inter-company lines should be invoiced or not')
    invoicing_type_message = fields.Char(string='Invoicing Type Message', compute='_compute_invoicing_type_message')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)

    @api.depends('purchase_order_id')
    def _compute_invoicing_type_message(self):
        """
        Compute wizard message to inform user whether there is invoiceable lines linked to an inter-company transaction or not
        """
        for wiz in self:
            msg = ''
            if wiz.purchase_order_id:
                intercompany_sale_order_lines = self.sudo().env['sale.order.line'].search([('inter_company_po_line_id', 'in', wiz.purchase_order_id.order_line.ids)])
                if intercompany_sale_order_lines <= 0:
                    msg = _('There is no invoiceable line for this purchase order.')
                else:
                    if not intercompany_sale_order_lines:
                        msg = _('No purchase order line is part of an inter-company transaction.')
                    elif all([line in intercompany_sale_order_lines.mapped('inter_company_po_line_id') for line in wiz.purchase_order_id.order_line]):
                        msg = _('All purchase order lines are linked to an inter-company transaction.')
                    else:
                        msg = _('Some purchase order lines are linked to an inter-company transaction.')
            wiz.invoicing_type_message = msg

    def action_create_vendor_bill(self):
        """
        Call 'Create Invoice' button method
        To prevent wizard to be displayed again, there is context information on button
        """
        self.ensure_one()
        if self.purchase_order_id:
            return self.purchase_order_id.action_view_invoice()
