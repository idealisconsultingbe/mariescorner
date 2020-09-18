# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_sale_order_line_data(self, line, company, sale_id):
        """ Overridden Method

            Generate the Sales Order Line values from the PO line.
            Add Stock product attribute values to SO Line values.
            :param line : the origin Purchase Order Line
            :rtype line : purchase.order.line record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param sale_id : the id of the SO
        """
        res = super(PurchaseOrder, self)._prepare_sale_order_line_data(line, company, sale_id)
        if line.product_no_variant_attribute_value_ids or line.product_custom_attribute_value_ids:
            res.update({
                'name': line.name,
                'product_no_variant_attribute_value_ids': [(6, 0, line.product_no_variant_attribute_value_ids.ids)],
                'product_custom_attribute_value_ids': [(6, 0, line.product_custom_attribute_value_ids.ids)],
                'comment': line.comment
            })
        return res
