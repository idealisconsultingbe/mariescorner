# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _get_sale_line(self):
        """
        Retrieve sale line from a move
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
        if self.move_dest_ids and len(self.move_dest_ids) == 1:
            return self.move_dest_ids[0]._get_sale_line()
        return False
