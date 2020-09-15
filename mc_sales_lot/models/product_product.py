# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sales_lot_activated = fields.Boolean(string='Sales Lot Activated', compute='_compute_sales_lot_activated', help='Technical field that indicates whether a '
                                                                                                                    'sales lot needs to be used for this product.')

    def _compute_sales_lot_activated(self):
        """
        Sales lot can be activated on category or on product.
        :return:    True if a sales lot should be used for this product.
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
