# -*- coding: utf-8 -*-

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
        if move_dest_ids and len(move_dest_ids.mapped('sale_line_id')) == 1 and all(move.sale_line_id for move in move_dest_ids):
            res.update({'name': move_dest_ids[0].sale_line_id.name, 'product_no_variant_attribute_value_ids': [(6, 0, move_dest_ids[0].sale_line_id.product_no_variant_attribute_value_ids.ids)]})
        return res