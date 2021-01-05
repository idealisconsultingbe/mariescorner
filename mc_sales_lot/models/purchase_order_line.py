# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Manufacturing Number', readonly=True, copy=False)
