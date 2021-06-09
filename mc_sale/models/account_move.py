# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        """
        If we modify the short name in the invoice_line_ids add it to the corresponding line_ids
        The standard pop the 'invoice_line_ids' of the vals dictionary.
        :return:
        """
        if vals.get('line_ids') and vals.get('invoice_line_ids'):
            for invoice_line in vals['invoice_line_ids']:
                if len(invoice_line) == 3 and invoice_line[2] and 'short_name' in invoice_line[2]:
                    id = invoice_line[1]
                    for line in vals['line_ids']:
                        if len(line) == 3 and line[1] == id:
                            line[2]['short_name'] = invoice_line[2]['short_name']
        res = super(AccountMove, self).write(vals)
        return res
