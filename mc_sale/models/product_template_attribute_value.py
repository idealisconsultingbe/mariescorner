# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    price_extra = fields.Float(compute='_compute_price_extra', store=True)
    manual_price_extra = fields.Float(
        string='Manual Value Price Extra',
        default=0.0,
        digits='Product Price',
        help='Manual extra price for the variant with this attribute value on sale price.')
    is_manual_price_extra = fields.Boolean(string='Manual Price', help='Used to prevent automatic computation of extra price', default=False)

    @api.depends(
        'product_tmpl_id.linear_length',
        'product_attribute_value_id.unit_price',
        'product_attribute_value_id.percentage_price_ids',
        'attribute_id.has_linear_price',
        'manual_price_extra',
        'is_manual_price_extra')
    def _compute_price_extra(self):
        """ compute extra price according to precedence rule:
        * Precedence rule -> manual price > linear price > percentage price
        -   if product template attribute value 'manual price' flag is on, then use price manually set by user
        -   else if product attribute value has 'linear price' flag set, then extra price should be 0.0 and computed later on.
                    Computed through the product configurator when the user has given the length used.
        -   else if product attribute value has a 'percentage price' matching product category,
                    apply this percentage on public price, else extra price should be 0.0
        -   else extra price is 0.0
        """
        for value in self:
            if value.is_manual_price_extra:
                price_extra = value.manual_price_extra
            elif value.product_attribute_value_id.has_linear_price:
                price_extra = 0.0
            elif value.product_attribute_value_id.percentage_price_ids:
                price_extra = 0.0
                percentage_price = value._get_percentage_price()
                if percentage_price and percentage_price.type == 'percentage':
                    price_extra = round(value.product_tmpl_id.list_price * percentage_price.percentage_price)
                elif percentage_price and percentage_price.type == 'amount':
                    price_extra = percentage_price.price_extra
            else:
                price_extra = 0.0
            value.price_extra = price_extra

    def _get_percentage_price(self):
        """ Retrieve applicable percentage rule according to matching category """
        # product_attribute_value_id is mandatory
        for percentage_price in self.product_attribute_value_id.percentage_price_ids.filtered(lambda p: p.percentage_price):
            category = self.product_tmpl_id.categ_id
            # search for a matching category through parents
            while category:
                if percentage_price.product_category_id == category:
                    return percentage_price
                else:
                    category = category.parent_id
        return False





