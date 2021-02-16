# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sales_lot_ids = fields.Many2many('stock.production.sales.lot', 'aml_sales_lot_rel', 'line_id', 'sales_lot_id', string='Manufacturing Numbers')
