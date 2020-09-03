# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        """ Overridden Method
            Add product attribute values from sale order line to purchase order line
        """
        res = super(StockRule, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, values, po)
        move_dest_ids = values.get('move_dest_ids', False)
        if move_dest_ids:
            sale_line = move_dest_ids[0]._get_sale_line()
            res.update({
                'name': sale_line.name,
                'product_no_variant_attribute_value_ids': [(6, 0, sale_line.product_no_variant_attribute_value_ids.ids)],
                'product_custom_attribute_value_ids': [(6, 0, sale_line.product_custom_attribute_value_ids.ids)],
                'comment': sale_line.comment
            })
        return res
