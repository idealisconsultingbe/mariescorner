# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sales_representative_id = fields.Many2one('res.partner', string='Sales Representative', domain=[('is_sales_representative', '=', True), '|', ('is_company', '=', True), ('type', '=', 'contact')])

    @api.onchange('partner_id')
    def _onchange_sales_representative_id(self):
        """ default sales representative is the one set on partner """
        if self.partner_id and self.partner_id.sales_representative_id:
            self.sales_representative_id = self.partner_id.sales_representative_id
        else:
            self.sales_representative_id = False

    def _prepare_invoice(self):
        """ Sales representative on invoices is the one set on sales order """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.sales_representative_id:
            invoice_vals['sales_representative_id'] = self.sales_representative_id.id
        return invoice_vals