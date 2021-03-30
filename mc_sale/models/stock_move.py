# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        """
        Overridde standard method -> add the manufacturing number into the procurement.
        :return:
        """
        values = super(StockMove, self)._prepare_procurement_values()
        if self.raw_material_production_id and self.raw_material_production_id.inter_company_origin:
            values['origin'] = self.raw_material_production_id.inter_company_origin
        return values


    def _get_purchase_line_id(self):
        """
        Go through the stock move chain in a up bottom way.
        Return the first purchase order line found.
        """
        current_move = self
        po_line = self.env['purchase.order.line']
        while current_move:
            if current_move.created_purchase_line_id:
                po_line = current_move.created_purchase_line_id
                current_move = self.env['stock.move']
            elif current_move.move_orig_ids:
                current_move = current_move.move_orig_ids[0]
            else:
                current_move = self.env['stock.move']
        return po_line

    def _get_sale_line(self):
        """
        Retrieve sale line from a stock move
        Return the sale_line only if it is link to attributes.
        """
        self.ensure_one()
        if self and self.sale_line_id:
            if self.sale_line_id.product_no_variant_attribute_value_ids:
                return self.sale_line_id
            elif self.sale_line_id.order_id:
                try:
                    order_line = self.sale_line_id.order_id.auto_purchase_order_id.order_line
                except Exception:
                    return False
                if order_line.move_dest_ids and len(order_line.move_dest_ids) == 1:
                    return order_line.move_dest_ids[0]._get_sale_line()
            else:
                return False
        if self.move_dest_ids and len(self.move_dest_ids) == 1:
            return self.move_dest_ids[0]._get_sale_line()
        return False

