# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    short_name = fields.Text(string='Short Description')

    def _product_id_change(self):
        super(PurchaseOrderLine, self)._product_id_change()
        self.short_name = self.name
