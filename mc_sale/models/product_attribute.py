# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    has_linear_price = fields.Boolean(string='Linear Price')
    tissue_category = fields.Selection([('tissue_1', 'Tissue 1'), ('tissue_2', 'Tissue 2')], string='Tissue Category', help='Tissue of category 1 will have their sale cost impacted by the field tissue meterage 1 on the sale product configurator.'
                                                                                                                            'Tissue of category 2 will have their sale cost impacted by the field tissue meterage 2 on the sale product configurator.')
