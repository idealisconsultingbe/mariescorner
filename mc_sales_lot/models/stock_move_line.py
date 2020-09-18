# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', related='move_id.sales_lot_id', string='Manufacturing Number')
