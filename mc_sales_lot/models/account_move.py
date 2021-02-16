# -*- coding: utf-8 -*-

from odoo import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Add manufacturing numbers on supplier invoice lines

        invoice lines (line_ids) are autocompleted and several fields are recomputed which may lead to a loss of information about manufacturing numbers.
        To prevent this, we add manufacturing numbers to values dictionnary of invoice lines.
        """
        for vals in vals_list:
            for line in vals.get('line_ids', []):
                line_values = line[2]
                purchase_line_id = line_values.get('purchase_line_id', False)
                if purchase_line_id:
                    purchase_line = self.env['purchase.order.line'].browse(purchase_line_id)
                    if purchase_line.sales_lot_id:
                        line_values['sales_lot_ids'] = [(4, purchase_line.sales_lot_id.id, 0)]
        res = super(AccountMove, self).create(vals_list)
        return res
