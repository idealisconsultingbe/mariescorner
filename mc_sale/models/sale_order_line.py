# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from .tools import to_float
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fabrics_meterage_needed = fields.Float(string='Meterage of fabrics', related='product_id.linear_length')
    product_sale_price = fields.Float(related='product_template_id.list_price', string='Standard Sale Price')
    comment = fields.Html(string='Comment')

    def _get_display_price(self, product):
        """ Overriden method

            Compute product price unit according to custom attribute values
            If there are custom values, then those values should be used
            to compute correct extra prices (attribute custom value * price unit of attribute value)
        """
        if self.product_custom_attribute_value_ids:
            custom_quantities = {value.custom_product_template_attribute_value_id.id: to_float(value.custom_value) for value in self.product_custom_attribute_value_ids}
            custom_product_template_attribute_value_ids = self.product_custom_attribute_value_ids.mapped('custom_product_template_attribute_value_id')

            # exclude product_template_attribute_values related to the same attribute than a custom attribute value
            no_variant_attributes_price_extra = [
                ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                    lambda ptav:
                    ptav.price_extra and
                    ptav.attribute_id not in custom_product_template_attribute_value_ids.mapped('attribute_id') and
                    ptav not in product.product_template_attribute_value_ids
                )
            ]
            # compute correct extra prices of custom attribute values
            no_variant_attributes_price_extra += [
                ptav.product_attribute_value_id.unit_price * custom_quantities[ptav.id] for ptav in
                custom_product_template_attribute_value_ids.filtered(
                    lambda ptav:
                    ptav.product_attribute_value_id.unit_price and
                    ptav not in product.product_template_attribute_value_ids
                )
            ]
            # following code is standard
            if no_variant_attributes_price_extra:
                product = product.with_context(
                    no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                )

            if self.order_id.pricelist_id.discount_policy == 'with_discount':
                return product.with_context(pricelist=self.order_id.pricelist_id.id).price
            product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,
                                   uom=self.product_uom.id)

            final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
                product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                               self.product_uom_qty,
                                                                                               self.product_uom,
                                                                                               self.order_id.pricelist_id.id)
            if currency != self.order_id.pricelist_id.currency_id:
                base_price = currency._convert(
                    base_price, self.order_id.pricelist_id.currency_id,
                    self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
            # negative discounts (= surcharge) are included in the display price
            return max(base_price, final_price)
        else:
            return super(SaleOrderLine, self)._get_display_price(product)
