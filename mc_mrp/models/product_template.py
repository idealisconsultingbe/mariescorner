# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _create_product_variant(self, combination, log_warning=False):
        """
        Override standard method.
        If only one product is return and if this product doesn't have internal reference.
        Fulfill its internal reference with its attribute values.
        """
        product = super(ProductTemplate, self)._create_product_variant(combination, log_warning)
        if product and len(product) == 1:
            default_code = ""
            if product.product_template_attribute_value_ids and not product.default_code:
                for pt_attribute in product.product_template_attribute_value_ids:
                    default_code = "{}/{}".format(default_code,
                                                  pt_attribute.product_attribute_value_id.name) if default_code else pt_attribute.product_attribute_value_id.name
                product.write({'default_code': default_code})
        return product