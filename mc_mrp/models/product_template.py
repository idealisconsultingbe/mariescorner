# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from .tools import to_float


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_fabric_price(self, combination, custom_quantities):
        """
        Previously this method was used to find the price of fabric product from the given combination.
        The variant price was used and multiplied by custom quantity.

        In order to not rethink the whole logic, we keep this method but use extra price from ptav instead,
        in the same way it is done for non-fabric attributes.

        :param combination: Product Template Attribute Values
        :param custom_quantities: {'attribute_id': qty} link a 'float' qty to an attribute
        :return: list of price for the given combination, ptav from the combination that has been used.
        """
        self.ensure_one()
        custom_extra_prices = []
        ptav_used = self.env['product.template.attribute.value']
        attribute_ids = combination.mapped('attribute_id.id')
        for ptav in combination:
            percentage_price_rule = ptav._get_percentage_price()
            if percentage_price_rule and percentage_price_rule.quantity_computation_type == 'total_quantity':
                price = ptav.price_extra * sum([custom_quantities.get(id, 0) for id in attribute_ids])
                ptav_used |= ptav
            elif percentage_price_rule and percentage_price_rule.quantity_computation_type == 'quantity':
                price = ptav.price_extra * custom_quantities.get(ptav.attribute_id.id, 0)
                ptav_used |= ptav
            custom_extra_prices.append(price)
        return custom_extra_prices, ptav_used

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
                # keep only custom attribute values linked to an attribute marked as linear price
                # attribute_id is mandatory for ptav
                combination_candidate = custom_combination.filtered(lambda ptav: ptav.id == ptav_id and ptav.attribute_id.has_linear_price)
                # since we filter by record id, there should be only one or zero result.
                if combination_candidate:
                    custom_quantities[combination_candidate.attribute_id.id] = pre_custom_quantities[ptav_id]

            # Find price of fabric product linked to this combination
            fabric_product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_fabric_product_id')
            fabric_product = self.env['product.template'].browse(int(fabric_product_id)) if fabric_product_id else False
            custom_extra_price = []
            ptav_used = self.env['product.template.attribute.value']
            if fabric_product:
                custom_extra_price, ptav_used = fabric_product.get_fabric_price(combination, custom_quantities)

            if product:
                # compute correct extra prices of custom attribute values left
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
                # FIXME : why do we use product.price ???
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
        Overridden standard method.
        If only one product is returned and if this product doesn't have internal reference.
        Fill its internal reference with its attribute values.
        """
        product = super(ProductTemplate, self)._create_product_variant(combination, log_warning)
        if product and len(product) == 1:
            default_code = ""
            if product.product_template_attribute_value_ids and not product.default_code:
                for pt_attribute in product.product_template_attribute_value_ids:
                    default_code = "{}/{}".format(default_code, pt_attribute.product_attribute_value_id.name) if default_code else pt_attribute.product_attribute_value_id.name
                product.write({'default_code': default_code})
        return product