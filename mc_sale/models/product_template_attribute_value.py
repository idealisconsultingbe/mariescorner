# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    price_extra = fields.Float(compute='_compute_price_extra')
    manual_price_extra = fields.Float(
        string='Manual Value Price Extra',
        default=0.0,
        digits='Product Price',
        help='Manual extra price for the variant with this attribute value on sale price.')
    is_manual_price_extra = fields.Boolean(string='Manual Price', help='Used to prevent automatic computation of extra price', default=False)

    @api.depends_context('force_company')
    def _compute_price_extra(self):
        """ compute extra price according to precedence rule:
        * Precedence rule -> manual price > linear price & custom value > percentage price > linear price  >  0.0
        -   if product template attribute value 'manual price' flag is on, then use price manually set by user
        -   else if product attribute has 'linear price' flag set,
            then extra price should be 0.0 and computed later on (computed through the product configurator when the user has given the length used: unit price * custom quantity).
        -   else if has a 'percentage price' matching product category,
            apply this percentage on public price,
        -   else extra price is 0.0
        """
        for value in self:
            price_extra = 0.0
            if value.is_manual_price_extra:
                price_extra = value.manual_price_extra
            elif value.product_attribute_value_id.has_linear_price:
                price_extra = 0.0
            elif value.product_attribute_value_id.percentage_price_ids:
                percentage_price = value._get_percentage_price()
                if percentage_price and percentage_price.type == 'percentage':
                    price_extra = round(value.product_tmpl_id.list_price * percentage_price.percentage_price)
                elif percentage_price and percentage_price.type == 'amount':
                    price_extra = percentage_price.price_extra
            value.price_extra = price_extra

    def _get_percentage_price(self):
        """ Retrieve applicable percentage rule according to matching category """
        # product_attribute_value_id is mandatory
        if "force_company" in self.env.context:
            company_id = self.env.context['force_company']
        else:
            company_id = self.env.company.id
        for percentage_price in self.product_attribute_value_id.percentage_price_ids.filtered(lambda p: (p.percentage_price or p.price_extra) and p.company_id.id == company_id):
            category = self.product_tmpl_id.categ_id
            # search for a matching category through parents
            while category:
                if percentage_price.product_category_id == category:
                    return percentage_price
                else:
                    category = category.parent_id
        return False
