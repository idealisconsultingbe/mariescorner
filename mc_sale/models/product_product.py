# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_fabric = fields.Boolean(string='Is a Fabric', compute='_compute_is_fabric', help='Technical field that indicates whether a product is a frabic.')

    def _compute_is_fabric(self):
        """
        Is fabric is activated on the product category.
        :return:    True if a product belongs to a fabric category.
                    False otherwise.
        """
        for product in self:
            fabric = False
            categ = product.categ_id
            while not fabric and categ:
                fabric = categ.is_fabric
                categ = categ.parent_id
            product.is_fabric = fabric
