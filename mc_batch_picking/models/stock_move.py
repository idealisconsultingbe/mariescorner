# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import float_compare


class StockMoveLine(models.Model):
    _inherit = 'stock.move'

    inter_company_batch_picking_name = fields.Char(string='Received From', compute='_get_intercompany_batch_name')

    def _get_intercompany_batch_name(self):
        """
        Get inter company batch picking name.
        """
        for sm in self:
            batch_name = ''
            if sm.move_line_ids:
                batch_name = ', '.join(sm.move_line_ids.mapped('inter_company_batch_picking_name'))
            sm.inter_company_batch_picking_name = batch_name
