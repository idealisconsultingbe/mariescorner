# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def post(self):
        """
        When posting an invoice, add an analytic account on each invoice lines with a manufacturing number but no analytic account
        A new analytic account is created if it does not already exist"""
        res = super(AccountMove, self).post()
        for move in self:
            for line in move.invoice_line_ids.filtered(lambda l: l.sales_lot_ids and not l.analytic_account_id):
                name = ' - '.join(line.sales_lot_ids.mapped('name'))
                analytic_account = self.env['account.analytic.account'].search([('name', '=', name)], limit=1)
                line.analytic_account_id = analytic_account if analytic_account else self.env['account.analytic.account'].create({'name': name, 'company_id': line.company_id.id})
        return res
