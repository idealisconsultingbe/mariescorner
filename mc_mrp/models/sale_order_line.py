# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from .tools import to_float
from odoo import api, fields, models, _
from odoo.tools import float_round


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # change label
    list_price = fields.Float(string='Base Price', digits='Product Price',
                              help='This is the product public price')

    # new fields
    list_price_extra = fields.Float(string='Public Price', compute='_compute_list_price_extra', digits='Product Price', store=True, copy=True,
                                    help='This is the product public price and the sum of the extra price of all attributes (with custom values)')
    delivery_date = fields.Date(related='sales_lot_id.delivery_date')
    fabric_date = fields.Date(related='sales_lot_id.fabric_date')

    @api.depends('product_no_variant_attribute_value_ids',
                 'product_id.product_template_attribute_value_ids',
                 'list_price')
    def _compute_list_price_extra(self):
        """
        Compute list_extra_price which is product price with extra and eventually a pricelist applied
        Removed 'product_custom_attribute_value_ids' from depends in order to prevent recomputation when order is sent to production
        (because product_custom_attribute_value_ids are lost)
        """
        for line in self:
            price = line.list_price
            extra_prices = line._get_no_variant_attributes_price_extra(line.product_id)
            if extra_prices:
                precision = self.env['decimal.precision'].precision_get('Product Price')
                price += float_round(sum(extra_prices), precision_digits=precision)
            line.list_price_extra = price

    @api.model
    def create(self, values):
        """
        Trigger the product_id_change right after the so_line creation if values contains the parameters 'trigger_product_id_onchange'
        """
        trigger_product_id_onchange = False
        if 'trigger_product_id_onchange' in values:
            trigger_product_id_onchange = values['trigger_product_id_onchange']
            del values['trigger_product_id_onchange']
        so_line = super(SaleOrderLine, self).create(values)
        if trigger_product_id_onchange:
            so_line.product_id_change()
        return so_line

    def _get_no_variant_attributes_price_extra(self, product):
        """
        Return a list with extra prices including custom values
        :param product: product with its context
        :return: list of extra prices
        """
        if self.product_custom_attribute_value_ids:
            custom_quantities = {value.custom_product_template_attribute_value_id.attribute_id.id: to_float(value.custom_value) for value in self.product_custom_attribute_value_ids}
            fabric_product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_fabric_product_id')
            fabric_product = self.env['product.template'].browse(int(fabric_product_id)) if fabric_product_id else False
            custom_extra_price = []
            ptav_used = self.env['product.template.attribute.value']
            if fabric_product:
                custom_extra_price, ptav_used = fabric_product.get_variant_price(self.product_no_variant_attribute_value_ids, custom_quantities, self.order_id.pricelist_id)

            # exclude product_template_attribute_values related to the same attribute than a custom attribute value
            no_variant_attributes_price_extra = [
                ptav.with_context(force_company=self.order_id.company_id.id).price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                    lambda ptav:
                    ptav.price_extra and
                    ptav.attribute_id not in ptav_used.mapped('attribute_id') and
                    ptav not in product.product_template_attribute_value_ids
                )
            ]
            # compute correct extra prices of custom fabric attribute values
            no_variant_attributes_price_extra += custom_extra_price
        else:
            no_variant_attributes_price_extra = [
                ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                    lambda ptav:
                    ptav.price_extra and
                    ptav not in product.product_template_attribute_value_ids
                )
            ]
        return no_variant_attributes_price_extra

    def _get_display_price(self, product):
        """ Overridden method

            Compute product price unit according to custom attribute values
            If there are custom values, then those values should be used
            to compute correct extra prices (attribute custom value * price unit of attribute value)
        """
        if self.product_custom_attribute_value_ids:
            no_variant_attributes_price_extra = self._get_no_variant_attributes_price_extra(product)
            # following code is standard
            if no_variant_attributes_price_extra:
                product = product.with_context(no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra))
            if self.order_id.pricelist_id.discount_policy == 'with_discount':
                return float_round(product.with_context(pricelist=self.order_id.pricelist_id.id).price, precision_digits=0)
            product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)

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
            return float_round(max(base_price, final_price), precision_digits=0)
        else:
            return super(SaleOrderLine, self)._get_display_price(product)
