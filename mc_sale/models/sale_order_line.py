# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from .tools import to_float
from odoo import api, fields, models
from odoo.tools.misc import get_lang


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fabrics_meterage_needed = fields.Float(string='Meterage of fabrics', related='product_id.linear_length')
    product_sale_price = fields.Float(related='product_template_id.list_price', string='Standard Sale Price')
    comment = fields.Text(string='Comment')
    short_name = fields.Text(string='Short Description')

    @api.onchange('product_id')
    def product_id_change(self):
        """
        Overridden method
        Update short description with product attributes flagged accordingly and description lines on product.template(related(
        """
        res = super(SaleOrderLine, self).product_id_change()

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        product_description = product.get_product_multiline_description_sale() if product.get_product_multiline_description_sale() else ""

        product_configuration = formatted_product_configuration = ""
        if self.product_custom_attribute_value_ids or self.product_no_variant_attribute_value_ids:
            custom_ptavs = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
            no_variant_ptavs = self.product_no_variant_attribute_value_ids._origin
            desc_line_ids = product.product_tmpl_id.description_line_ids
            desc_line_attributes = self.env['product.attribute']
            if desc_line_ids:
                pacvs = self.product_custom_attribute_value_ids
                no_custom_ptavs = no_variant_ptavs - custom_ptavs
                desc_line_attributes = desc_line_ids.mapped('value_ids').mapped('attribute_id')
                for line in desc_line_ids:
                    formatted_product_values = []
                    for value in line.value_ids:
                        if value.type == 'text':
                            formatted_product_values.append(value.with_context(lang=self.order_id.partner_id.lang).text)
                        else:
                            if value.attribute_id in pacvs.mapped('custom_product_template_attribute_value_id').mapped('attribute_id'):
                                for pacv in pacvs.filtered(lambda p: p.custom_product_template_attribute_value_id.attribute_id == value.attribute_id):
                                    # formatted_product_values.append(pacv.with_context(lang=self.order_id.partner_id.lang).display_name)
                                    formatted_product_values.append(pacv.with_context(lang=self.order_id.partner_id.lang).custom_product_template_attribute_value_id.name)
                            elif value.attribute_id in no_custom_ptavs.mapped('attribute_id'):
                                for ptav in no_custom_ptavs.filtered(lambda p: p.attribute_id == value.attribute_id):
                                    # formatted_product_values.append(ptav.with_context(lang=self.order_id.partner_id.lang).display_name)
                                    formatted_product_values.append(ptav.with_context(lang=self.order_id.partner_id.lang).name)
                    formatted_product_configuration = '{}{}{}'.format(formatted_product_configuration, '\n', ' '.join(formatted_product_values))

            # display the no_variant attributes, except those that are also
            # displayed by a custom (avoid duplicate description)
            # select only those that should be displayed in short description
            for ptav in (no_variant_ptavs - custom_ptavs).filtered(lambda p: p.attribute_id.display_short_description and p.attribute_id not in desc_line_attributes):
                product_configuration += '\n' + ptav.with_context(lang=self.order_id.partner_id.lang).display_name

            # display the is_custom values
            # select only those that should be displayed in short description
            for pacv in self.product_custom_attribute_value_ids.filtered(lambda p: p.custom_product_template_attribute_value_id.attribute_id.display_short_description and p.custom_product_template_attribute_value_id.attribute_id not in desc_line_attributes):
                product_configuration += '\n' + pacv.with_context(lang=self.order_id.partner_id.lang).display_name

        self.update({'short_name': '{}\n{}{}'.format(product_description, formatted_product_configuration, product_configuration)})
        return res

    def _get_display_price(self, product):
        """ Overridden method

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
