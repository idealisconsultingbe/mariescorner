# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    short_name = fields.Text(string='Short Description')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ Overridden method """
        res = super(AccountMoveLine, self)._onchange_product_id()
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue
            line.short_name = line._get_computed_name()
        return res
