# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tissue_meterage_1 = fields.Float(string="Meterage of tissue 1", default=-1)
    tissue_meterage_2 = fields.Float(string="Meterage of tissue 2", default=0.0)
    product_sale_price = fields.Float(related="product_template_id.list_price", string="Standard Sale Price")
    comment = fields.Html(string="Comment")

    @api.onchange('product_id')
    def onchange_load_tisssue_meterage_1(self):
        """
        Tailor made product doesn't have default tissue meterage 1. It will change for every sale.
        Need to be filled in by the user!
        :return:
        """
        # We do this check because we want to execute this method just once! After the first time the value will be change by the sale product configurator.
        if self.product_id and self.tissue_meterage_1 == -1:
            self.tissue_meterage_1 = 0.0 if self.product_id.tailor_made else self.product_id.linear_length
        elif not self.product_id:
            self.tissue_meterage_1 = -1
