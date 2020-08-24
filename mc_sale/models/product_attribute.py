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
            self.value_ids.write({'is_custom': True})
        else:
            self.value_ids.write({'is_custom': False})
