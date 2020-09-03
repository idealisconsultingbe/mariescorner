# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.variant import VariantController


class CustomVariantController(VariantController):

    @http.route(['/sale/get_combination_info'], type='json', auth="user", methods=['POST'])
    def get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
        """
        Override the standard method.
        Handle the custom values sent by the JS in order to calculate the price depending on the meterage given in input by the user.
        """
        if not kw.get('custom_values'):
            return super(CustomVariantController, self).get_combination_info(product_template_id, product_id, combination, add_qty, pricelist_id, **kw)
        else:
            combination = request.env['product.template.attribute.value'].browse(combination)
            pricelist = self._get_pricelist(pricelist_id)
            ProductTemplate = request.env['product.template']
            if 'context' in kw: ProductTemplate = ProductTemplate.with_context(**kw.get('context'))
            product_template = ProductTemplate.browse(int(product_template_id))
            res = product_template._get_combination_info(combination, int(product_id or 0), int(add_qty or 1), pricelist, custom_values=kw.get('custom_values'))
            if 'parent_combination' in kw:
                parent_combination = request.env['product.template.attribute.value'].browse(kw.get('parent_combination'))
                if not combination.exists() and product_id:
                    product = request.env['product.product'].browse(int(product_id))
                    if product.exists():
                        combination = product.product_template_attribute_value_ids
                res.update({
                    'is_combination_possible': product_template._is_combination_possible(combination=combination,
                                                                                         parent_combination=parent_combination),
                })
            return res