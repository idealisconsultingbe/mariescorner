# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    has_linear_price = fields.Boolean(string='Linear Price')
    default_linear_value = fields.Boolean(string='Default Linear Value', default=False,
                                          help='Pre-filled the linear length in the produt configurator with the linear length defined on the product form view.')
    display_short_description = fields.Boolean(string='Show in Short Description', default=False,
                                               help='This information will be visible in short description of '
                                                    'a sale order line or a purchase order line after product configuration')

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
