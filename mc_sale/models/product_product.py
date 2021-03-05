# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_tcl = fields.Boolean(string='Is a TCL Fabric', compute='_compute_is_tcl', help='Technical field that indicates whether a product is a TCL fabric or not.')

    def _compute_category_mc_type(self):
        """
        :return:    True if a product has at least one attribute marked as TCL.
        """
        for product in self:
            is_tcl = False
            if product.product_template_attribute_value_ids:
                is_tcl = any(product.product_template_attribute_value_ids.mapped('product_attribute_value_id.is_tcl_value'))
            product.is_tcl = is_tcl
