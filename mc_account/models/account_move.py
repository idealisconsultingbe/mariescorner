# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def post(self):
        res = super(AccountMove, self).post()
        for move in self:
            for line in move.invoice_line_ids.filtered(lambda l: l.sales_lot_ids and not l.analytic_account_id):
                name = ' - '.join(line.sales_lot_ids.mapped('name'))
                line.analytic_account_id = self.env['account.analytic.account'].create({'name': name, 'company_id': line.company_id.id})
        return res
