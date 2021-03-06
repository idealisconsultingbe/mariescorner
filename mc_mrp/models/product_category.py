# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_foot = fields.Boolean(string='Is a foot Category', default=False,help='All products of this category will be see as being a foot')
