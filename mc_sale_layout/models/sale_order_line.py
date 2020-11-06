# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    base_price_unit = fields.Float(string='Public Unit Price', related='product_id.lst_price', digits='Product Price', default=0.0)
    price_unit = fields.Float(string='Customer Unit Price')
