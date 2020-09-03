# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', compute='_compute_sales_lot_id', string='Sales Lot',
                                   store=True)

    @api.depends('move_dest_ids.sales_lot_id')
    def _compute_sales_lot_id(self):
        """ Compute M2o relation to Stock Production Sales Lot from destination moves
        """
        for production in self:
            if len(production.move_dest_ids.mapped('sales_lot_id')) == 1 and all(
                    move.sales_lot_id for move in production.move_dest_ids):
                production.sales_lot_id = production.move_dest_ids[0].sales_lot_id
            else:
                production.sales_lot_id = False
