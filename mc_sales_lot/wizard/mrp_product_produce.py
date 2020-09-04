# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.model
    def default_get(self, fields):
        """
        Fill automatically lot/serial number in current view after creating them only if production has
        a Sales Lot in its moves
        """
        res = super(MrpProductProduce, self).default_get(fields)
        production = self.env['mrp.production']
        production_id = self.env.context.get('default_production_id') or self.env.context.get('active_id')
        if production_id:
            production = self.env['mrp.production'].browse(production_id)
        # Check whether the product use sales lot and needs lot or SN.
        if production.exists() and production.product_id.tracking != 'none' and production.product_id.sales_lot_activated:
            if 'finished_lot_id' in fields:
                # Creates automatically SN or Lot corresponding to the sales lot.
                if len(production.move_dest_ids.mapped('sales_lot_id')) == 1 and all(move.sales_lot_id for move in production.move_dest_ids):
                    sale_lot = production.move_dest_ids[0].sales_lot_id
                    # If the tracking is lot then the stock.production.lot must have the same name as the sales lot.
                    if production.product_id.tracking == 'lot':
                        lot_name = sale_lot.name
                        finished_lot_id = self.env['stock.production.lot'].search([('name', '=', sale_lot.name), ('product_id', '=', production.product_id.id)])
                    # If the tracking is serial then the stock.production.lot must have as name the sales lot + one increment.
                    # e.g: Sales Lot is 000001 then serial number should be -> 00000101, 00000102, 00000103...
                    else:
                        numbers_to_add = self.env['ir.config_parameter'].sudo().get_param('mc_sales_lot.additional_serial_number')
                        increment = len(production.finished_move_line_ids.sorted(key=lambda fml: fml.product_id == production.product_id and fml.sales_lot_id == sale_lot)) + 1
                        lot_name = sale_lot.name + str(increment).zfill(int(numbers_to_add))
                        finished_lot_id = self.env['stock.production.lot'].search([('name', '=', lot_name), ('product_id', '=', production.product_id.id)])
                        move_line_using_lot = self.env['stock.move.line'].search([('lot_id', '=', finished_lot_id.id), ('product_id', '=', production.product_id.id)])
                        while finished_lot_id and move_line_using_lot:
                            increment += 1
                            lot_name = sale_lot.name + str(increment).zfill(int(numbers_to_add))
                            finished_lot_id = self.env['stock.production.lot'].search([('name', '=', lot_name), ('product_id', '=', production.product_id.id)])
                            move_line_using_lot = self.env['stock.move.line'].search([('lot_id', '=', finished_lot_id.id), ('product_id', '=', production.product_id.id)])
                    if not finished_lot_id:
                        finished_lot_id = self.env['stock.production.lot'].create({
                            'name': lot_name,
                            'product_id': production.product_id.id,
                            'company_id': production.company_id.id
                        })
                    res['finished_lot_id'] = finished_lot_id.id
        return res
