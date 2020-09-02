# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    use_sales_lot = fields.Boolean(string='Use Sales Lot', default=False)
    sales_lot_activated = fields.Boolean(string='Sales Lot Activated', compute='_compute_sales_lot_activated', help='Technical fields that tells whether a '
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

