# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    inter_company_po_line_id = fields.Many2one('purchase.order.line', string='InterCompany Purchase Order Line', help='Purchase order line that created current sale order line in an intercompany logic')

