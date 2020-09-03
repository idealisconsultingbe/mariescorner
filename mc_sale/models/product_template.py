# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from .tools import to_float
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_length_uom(self):
        return self.get_length_uom_name()

    tailor_made = fields.Boolean(string='Is Tailor Made', default=False)
    linear_length = fields.Float('Linear Length', digits='Product Unit of Measure', default=0.0, help='Quantity of fabric required to upholster furniture')
    length_uom_name = fields.Char(string='Length UoM Label', compute='_compute_length_uom_name', default=_default_length_uom, store=True)

    def _compute_length_uom_name(self):
        for template in self:
            template.length_uom_name = self.get_length_uom_name()

    @api.model
    def get_length_uom_name(self):
        """ Retrieve reference uom name for length measures.
        It is possible to change this easily to use uom from ir.config.parameter for example """
        uom = self.env.ref('uom.product_uom_meter', False) or self.env['uom.uom'].search(
            [('measure_type', '=', 'length'), ('uom_type', '=', 'reference')], limit=1)
        return uom.name

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False, **kw):
        """ Overridden method used in product configurator
            If configurator uses custom values then compute extra prices according to them
            (attribute custom value * price unit of attribute value)
        """
        self.ensure_one()
        res = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination, only_template)

        if kw.get('custom_values'):
            # dict of quantities
            custom_quantities = {value['custom_product_template_attribute_value_id']: to_float(value['custom_value']) for value in kw.get('custom_values')}

            # standard
            context = dict(self.env.context, quantity=self.env.context.get('quantity', add_qty), pricelist=pricelist.id if pricelist else False)
            product_template = self.with_context(context)
            product = product_template.env['product.product'].browse(res.get('product_id'))
            combination = combination or product_template.env['product.template.attribute.value']
            if not product_id and not combination and not only_template:
                combination = product_template._get_first_possible_combination(parent_combination)

            # retrieve product template attribute values bound to custom values in order to remove them from price extra computation
            custom_combination = product_template.env['product.template.attribute.value'].browse([value['custom_product_template_attribute_value_id'] for value in kw.get('custom_values')])
            combination = combination - custom_combination

            if product:
                no_variant_attributes_price_extra = [
                    ptav.price_extra for ptav in combination.filtered(
                        lambda ptav:
                        ptav.price_extra and
                        ptav not in product.product_template_attribute_value_ids
                    )
                ]
                # compute correct extra prices of custom attribute values
                no_variant_attributes_price_extra += [
                    ptav.product_attribute_value_id.unit_price * custom_quantities[ptav.id] for ptav in custom_combination.filtered(
                        lambda ptav:
                        ptav.product_attribute_value_id.unit_price and
                        ptav not in product.product_template_attribute_value_ids
                    )
                ]
                # standard
                if no_variant_attributes_price_extra:
                    product = product.with_context(
                        no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                    )
                list_price = product.price_compute('list_price')[product.id]
                price = product.price if pricelist else list_price
            else:
                # FIXME: is this necessary ? We apply the same logic on product template
                current_attributes_price_extra = [v.price_extra or 0.0 for v in combination]
                current_attributes_price_extra += [v.product_attribute_value_id.unit_price * custom_quantities[v.id] for v in custom_combination]
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
