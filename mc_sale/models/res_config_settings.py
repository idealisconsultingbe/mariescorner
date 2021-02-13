# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fabric_default_product_id = fields.Many2one('product.template', string='Fabric Product', domain="[('type', '=', 'product')]",
                                                config_parameter='sale.default_fabric_product_id', help='Default product used for fabric features')
