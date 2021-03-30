# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sales_lot_ids = fields.Many2many('stock.production.sales.lot', 'aml_sales_lot_rel', 'line_id', 'sales_lot_id', string='Manufacturing Numbers')
    sale_lot_id = fields.Many2one('stock.production.sales.lot', string='Manufacturing Number', store=True, compute='_compute_sale_lot_id')

    @api.depends('sales_lot_ids')
    def _compute_sale_lot_id(self):
        """
        It should be impossible to merge manufacturing numbers on one invoice line.
        Thus there is only one manufacturing number by line. Otherwise, retrieve the first one.
        """
        for line in self:
            line.sale_lot_id = line.sales_lot_ids[0] if len(line.sales_lot_ids) > 1 else line.sales_lot_ids
