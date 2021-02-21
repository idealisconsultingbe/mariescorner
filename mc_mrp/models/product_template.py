# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from .tools import to_float


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def get_combination_qty(self, custom_quantities, ptav_combination):
        qty = 0
        for ptav in ptav_combination:
            if custom_quantities.get(ptav.attribute_id.id, False):
                qty = custom_quantities[ptav.attribute_id.id]
                break
        return qty

    def get_combination_fabric_attributes(self):
        """
        Get attributes related to the fabric product.
        """
        self.ensure_one()
        combination_fabric_attribute = {}
        for attribute_line in self.attribute_line_ids:
            corresponding_attributes = attribute_line.attribute_id.product_attribute_ids
            i = 1
            for attribute in corresponding_attributes:
                if combination_fabric_attribute.get(i, False):
                    combination_fabric_attribute[i] |= attribute
                else:
                    combination_fabric_attribute[i] = attribute
                i += 1
        return combination_fabric_attribute

    def get_combination_fabric_product_template_attribute_values(self, combination, custom_quantities):
        """
        Map qty and ptav of the fabric product
        :param combination: Product Template Attribute Values
        :param custom_quantities: {'attribute_id': qty} link an qty 'float' to an attribute
        :return:
        """
        self.ensure_one()
        product_template_attribute_values_combination = []
        combination_fabric_attributes = self.get_combination_fabric_attributes()
        product_no_variant_attribute_values_link_fabric = combination.filtered(lambda ptav: ptav.attribute_id.product_attribute_id in self.attribute_line_ids.attribute_id)
        for combination_id in combination_fabric_attributes:
            arg_ptav = product_no_variant_attribute_values_link_fabric.filtered(lambda ptav: ptav.attribute_id in combination_fabric_attributes[combination_id])
            fabric_product_attribute_values = arg_ptav.mapped('product_attribute_value_id.product_attribute_value_id')
            qty = self.get_combination_qty(custom_quantities, arg_ptav)
            fabric_ptav = self.env['product.template.attribute.value'].search([('product_tmpl_id', '=', self.id),
                                                                               ('product_attribute_value_id', 'in', fabric_product_attribute_values.ids)])
            product_template_attribute_values_combination.append([arg_ptav, fabric_ptav, qty])
        return product_template_attribute_values_combination

    def get_variant_price(self, combination, custom_quantities, pricelist=False):
        """
        Method used to found the price of fabric product from the given combination.
        :param combination: Product Template Attribute Values
        :param custom_quantities: {'attribute_id': qty} link an qty 'float' to an attribute
        :return: list of price for the combination given, ptav from the combination that have been used.
        """
        self.ensure_one()
        product_template_attribute_values_link_to_self = self.env['product.template.attribute.value']
        custom_extra_price = []
        product_template_attribute_values_combination = self.get_combination_fabric_product_template_attribute_values(combination, custom_quantities)
        for arg_ptav_combination, fabric_ptav_combination, qty in product_template_attribute_values_combination:
            if all(fabric_ptav_combination.mapped('product_attribute_value_id.is_none_value')):
                price = 0
            else:
                fabric_product_variant = self._create_product_variant(fabric_ptav_combination)
                if pricelist:
                    price = fabric_product_variant.with_context(pricelist=pricelist.id).price
                else:
                    price = fabric_product_variant.price
            custom_extra_price.append(price * qty)
            product_template_attribute_values_link_to_self |= arg_ptav_combination
        return custom_extra_price, product_template_attribute_values_link_to_self

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False, **kw):
        """ Overridden method used in product configurator
            If configurator uses custom values then compute extra prices according to them
            (attribute custom value * price unit of attribute value)
        """
        combination = combination.with_context(self.env.context)
        self.ensure_one()
        res = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination, only_template)

        if kw.get('custom_values'):
            # standard
            context = dict(self.env.context, quantity=self.env.context.get('quantity', add_qty), pricelist=pricelist.id if pricelist else False)
            product_template = self.with_context(context)
            product = product_template.env['product.product'].browse(res.get('product_id'))
            combination = combination or product_template.env['product.template.attribute.value']
            if not product_id and not combination and not only_template:
                combination = product_template._get_first_possible_combination(parent_combination)

            # dict of quantities
            custom_combination = product_template.env['product.template.attribute.value'].browse([value['custom_product_template_attribute_value_id'] for value in kw.get('custom_values')])
            pre_custom_quantities = {value['custom_product_template_attribute_value_id']: to_float(value['custom_value']) for value in kw.get('custom_values')}
            custom_quantities = {}
            for ptav_id in pre_custom_quantities:
                custom_quantities[custom_combination.filtered(lambda ptav: ptav.id == ptav_id).attribute_id.id] = pre_custom_quantities[ptav_id]


            # Find price of fabric product linked to this combination
            fabric_product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_fabric_product_id')
            fabric_product = self.env['product.template'].browse(int(fabric_product_id)) if fabric_product_id else False
            custom_extra_price = []
            ptav_used = self.env['product.template.attribute.value']
            if fabric_product:
                custom_extra_price, ptav_used = fabric_product.get_variant_price(combination, custom_quantities, pricelist)

            # Keeps only custom attribute values linked to an attribute marked as linear price and for which the manual extra price is not activated.
            if product:
                # compute correct extra prices of custom attribute values
                no_variant_attributes_price_extra = [
                    ptav.price_extra for ptav in combination.filtered(
                        lambda ptav:
                        ptav.price_extra and
                        ptav.attribute_id not in ptav_used.mapped('attribute_id') and
                        ptav not in product.product_template_attribute_value_ids
                    )
                ]
                # compute correct extra prices of custom fabric attribute values
                no_variant_attributes_price_extra += custom_extra_price
                # standard
                if no_variant_attributes_price_extra:
                    product = product.with_context(
                        no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                    )
                list_price = product.price_compute('list_price')[product.id]
                price = product.price if pricelist else list_price
            else:
                current_attributes_price_extra = [v.price_extra or 0.0 for v in (combination - ptav_used)]
                current_attributes_price_extra += custom_extra_price
                # standard
                product_template = product_template.with_context(current_attributes_price_extra=current_attributes_price_extra)
                list_price = product_template.price_compute('list_price')[product_template.id]
                price = product_template.price if pricelist else list_price

            # standard
            if pricelist and pricelist.currency_id != product_template.currency_id:
                list_price = product_template.currency_id._convert(
                    list_price, pricelist.currency_id, product_template._get_current_company(pricelist=pricelist),
                    fields.Date.today()
                )
            # standard
            price_without_discount = list_price if pricelist and pricelist.discount_policy == 'without_discount' else price
            has_discounted_price = (pricelist or product_template).currency_id.compare_amounts(price_without_discount,price) == 1
            res.update({'price': price, 'list_price': list_price, 'has_discounted_price': has_discounted_price})

        return res

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
                    default_code = "{}/{}".format(default_code, pt_attribute.product_attribute_value_id.name) if default_code else pt_attribute.product_attribute_value_id.name
                product.write({'default_code': default_code})
        return product