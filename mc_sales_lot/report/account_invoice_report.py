# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', 'Manufacturing Number', readonly=True)

    @api.model
    def _select(self):
        res = super(AccountInvoiceReport, self)._select()
        return res + ', line.sale_lot_id as sales_lot_id'

    @api.model
    def _group_by(self):
        res = super(AccountInvoiceReport, self)._group_by()
        return res + ', line.sale_lot_id'
