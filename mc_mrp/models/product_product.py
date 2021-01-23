# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_fabric = fields.Boolean(string='Is a Fabric', compute='_compute_category_mc_type', help='Technical field that indicates whether a product is a frabic.')
    is_foot = fields.Boolean(string='Is a Fabric', compute='_compute_category_mc_type', help='Technical field that indicates whether a product is a foot.')

    def _compute_category_mc_type(self):
        """
        Is fabric is activated on the product category.
        Is foot is activated on the product category.
        :return:    True if a product belongs to a fabric/foot category.
                    False otherwise.
        """
        for product in self:
            fabric = False
            foot = False
            categ = product.categ_id
            while not fabric and categ:
                fabric = categ.is_fabric
                categ = categ.parent_id
            categ = product.categ_id
            while not foot and categ:
                foot = categ.is_foot
                categ = categ.parent_id
            product.is_fabric = fabric
            product.is_foot = foot
