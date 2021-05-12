# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    sales_representative_id = fields.Many2one('res.partner', 'Sales Representative', readonly=True)

    @api.model
    def _select(self):
        res = super(AccountInvoiceReport, self)._select()
        return res + ', move.sales_representative_id as sales_representative_id'

    @api.model
    def _group_by(self):
        res = super(AccountInvoiceReport, self)._group_by()
        return res + ', move.sales_representative_id'
