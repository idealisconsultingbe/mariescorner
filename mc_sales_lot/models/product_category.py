# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    use_sales_lot = fields.Boolean(string='Use Sales Lot', default=False, help='All product of this category will use a sales lot!')
