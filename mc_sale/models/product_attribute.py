# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    has_linear_price = fields.Boolean(string='Linear Price')

    @api.onchange('has_linear_price')
    def onchange_linear_price(self):
        """
        An attribute with a linear price should only have custom values in order to let the user indicate the meterage needed.
        """
        if self.has_linear_price:
            not_none_value = self.value_ids.filtered(lambda v: not v.is_none_value)
            not_none_value.write({'is_custom': True})
            (self.value_ids - not_none_value).write({'is_custom': False})
        else:
            self.value_ids.write({'is_custom': False})
