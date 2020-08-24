# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import ValidationError


def is_float(string_value):
    try:
        float(string_value)
        return True
    except ValueError:
        return False


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    @api.model
    def create(self, values):
        if values.get('custom_value'):
            values['custom_value'] = values['custom_value'].replace(',', '.')
        return super(ProductAttributeCustomValue, self).create(values)

    def write(self, values):
        if values.get('custom_value'):
            values['custom_value'] = values['custom_value'].replace(',', '.')
        return super(ProductAttributeCustomValue, self).write(values)

    @api.constrains('custom_value')
    def check_custom_value_formant(self):
        for custom_attribute in self:
            if custom_attribute.custom_product_template_attribute_value_id.attribute_id.has_linear_price and custom_attribute.custom_value:
                attribute = custom_attribute.custom_product_template_attribute_value_id.attribute_id
                custom_value = custom_attribute.custom_value.replace(',', '.')
                if not is_float(custom_value):
                    raise ValidationError(_("The custom value for the attribute '{}' should be a float. Something like 2.25 or 2,25. But your input is {}.".format(attribute.name, custom_attribute.custom_value)))
