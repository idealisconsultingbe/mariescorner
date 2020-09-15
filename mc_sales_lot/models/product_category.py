# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    use_sales_lot = fields.Boolean(string='Use Sales Lot', default=False, help='All products of this category will use a sales lot!')
