# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sales_lot_activated = fields.Boolean(string='Manufacturing Number Activated', compute='_compute_sales_lot_activated', help='Technical field that indicates whether a '
                                                                                                                               'manufacturing number needs to be used for this product.')

    def _compute_sales_lot_activated(self):
        """
        manufacturing number can be activated on categories or on products.
        :return:    True if a manufacturing number should be used for this product.
                    False otherwise.
        """
        for product in self:
            active = False
            categ = product.categ_id
            if product.use_sales_lot:
                active = True
            while not active and categ:
                active = categ.use_sales_lot
                categ = categ.parent_id
            product.sales_lot_activated = active
