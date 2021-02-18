# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Manufacturing Number')

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        """
        Overriden method
        Add the sales lot if into the dictionary of values
        """
        values = super(InventoryLine, self)._get_move_values(qty, location_id, location_dest_id, out)
        if self.sales_lot_id:
            values['sales_lot_id'] = self.sales_lot_id.id
        return values
