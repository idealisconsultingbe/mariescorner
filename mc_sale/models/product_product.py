# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    hs_code = fields.Char(string="HS Code", help="Standardized code for international shipping and goods declaration. At the moment, only used for the FedEx shipping provider.",)
    is_tcl = fields.Boolean(string='Is a TCL Fabric', compute='_compute_is_tcl', store=True, help='Technical field that indicates whether a product is a TCL fabric or not.')

    @api.depends('product_template_attribute_value_ids.product_attribute_value_id.is_tcl_value')
    def _compute_is_tcl(self):
        """
        :return:    True if a product has at least one attribute marked as TCL.
        """
        for product in self:
            is_tcl = False
            if product.product_template_attribute_value_ids:
                is_tcl = any(product.product_template_attribute_value_ids.mapped('product_attribute_value_id.is_tcl_value'))
            product.is_tcl = is_tcl
