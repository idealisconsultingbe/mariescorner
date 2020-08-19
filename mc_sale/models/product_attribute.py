# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    has_linear_price = fields.Boolean(string='Linear Price')
    tissue_category = fields.Selection([('tissue_1', 'Tissue 1'), ('tissue_2', 'Tissue 2')], string='Tissue Category', help='Tissue of category 1 will have their sale cost impacted by the field tissue meterage 1 on the sale product configurator.'
                                                                                                                            'Tissue of category 2 will have their sale cost impacted by the field tissue meterage 2 on the sale product configurator.')

    @api.onchange('has_linear_price')
    def onchange_reset_tissue_category(self):
        """
        Only product attribute that has a linear price could have a tissue category.
        """
        if not self.has_linear_price:
            self.tissue_category = False
