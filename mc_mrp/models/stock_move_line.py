# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Automatically create a lot if the context ask to
        """
        for val in vals_list:
            if self.env.context.get('operations_create_lot', False) and not val.get('lot_id') and not val.get('lot_name'):
                company = self.env['res.company']
                if val.get('move_id'):
                    move = self.env['stock.move'].browse(val['move_id'])
                    company = move.company_id
                elif val.get('picking_id'):
                    picking = self.env['stock.picking'].browse(val['picking_id'])
                    company = picking.company_id
                if val.get('product_id') and company:
                    lot = self.env['stock.production.lot'].create({'product_id': val['product_id'],
                                                                   'company_id': company.id})
                    val['lot_name'] = lot.name
                    val['lot_id'] = lot.id
        return super(StockMoveLine, self).create(vals_list)
