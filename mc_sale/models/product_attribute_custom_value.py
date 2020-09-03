# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from .tools import is_float
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    @api.model
    def create(self, values):
        """
        Replace comma by a '.' in order to be able to cast it into an int.
        This way the user can give as value 2,25 and we will still be able to cast it.
        """
        if values.get('custom_value'):
            values['custom_value'] = values['custom_value'].replace(',', '.')
        return super(ProductAttributeCustomValue, self).create(values)

    def write(self, values):
        """
        Replace comma by a '.' in order to be able to cast it into an int.
        This way the user can give as value 2,25 and we will still be able to cast it.
        """
        if values.get('custom_value'):
            values['custom_value'] = values['custom_value'].replace(',', '.')
        return super(ProductAttributeCustomValue, self).write(values)

    @api.constrains('custom_value')
    def _check_custom_value_format(self):
        """
        Make sure that custom value used for the meterage can be cast into a float.
        If not we block the user and ask him to give as input a correct format.
        """
        for custom_attribute in self:
            if custom_attribute.custom_product_template_attribute_value_id.attribute_id.has_linear_price and custom_attribute.custom_value:
                attribute = custom_attribute.custom_product_template_attribute_value_id.attribute_id
                custom_value = custom_attribute.custom_value.replace(',', '.')
                if not is_float(custom_value):
                    raise ValidationError(_("The custom value for the attribute '{}' should be a float like 2.25 or 2,25 (your input is {}).".format(attribute.name, custom_attribute.custom_value)))
