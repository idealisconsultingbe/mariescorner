# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductionSalesLot(models.Model):
    _inherit = 'stock.production.sales.lot'

    mc_care_warranty = fields.Boolean(string='Warranty Activated')
    final_partner_id = fields.Many2one('res.partner', string='Final Customer')
    mc_care = fields.Boolean(string='MC Care', compute='_compute_is_mc_care', store=True)

    @api.depends('origin_sale_order_line_id.product_no_variant_attribute_value_ids')
    def _compute_is_mc_care(self):
        """
        MC Care is set if at least one product.template.attribute.value of type 'mc care' is not a 'none' value.
        """
        for sale_lot in self:
            so_line = sale_lot.origin_sale_order_line_id
            mc_care = False
            if so_line:
                # Get all product.template.attribute.value of type mc care linked to this sale_lot
                ptavs_mc_care = so_line.product_no_variant_attribute_value_ids.filtered(lambda ptav: ptav.attribute_id.is_mc_care)
                # Check if at least one of them has not a 'none' value.
                if any(ptavs_mc_care.mapped(lambda ptav: not ptav.product_attribute_value_id.is_none_value)):
                    mc_care = True
            sale_lot.mc_care = mc_care

