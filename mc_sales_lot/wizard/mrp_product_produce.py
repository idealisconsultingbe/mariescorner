# -*- coding: utf-8 -*-

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
        if production.exists() and production.product_id.tracking != 'none':
            # increment = self.env.context.get('default_serial_increment')
            # if 'serial_increment' in fields:
            #     res['serial_increment'] = increment or 1
            if 'finished_lot_id' in fields:
                if len(production.move_dest_ids.mapped('sales_lot_id')) == 1 and all(
                        move.sales_lot_id for move in production.move_dest_ids):
                    sale_lot = production.move_dest_ids[0].sales_lot_id
                    if production.product_id.tracking == 'lot':
                        lot_name = sale_lot.name
                        finished_lot_id = self.env['stock.production.lot'].search([('name', '=', sale_lot.name), ('product_id', '=', self.product_id.id)])
                    else:
                        numbers_to_add = self.env['ir.config_parameter'].sudo().get_param('mc_sale.additional_serial_number')
                        increment = len(production.finished_move_line_ids.sorted(
                            key=lambda fml: fml.product_id == self.product_id and fml.sales_lot_id == sale_lot)) + 1
                        lot_name = sale_lot.name + str(increment).zfill(int(numbers_to_add))
                        finished_lot_id = self.env['stock.production.lot'].search([('name', '=', lot_name), ('product_id', '=', self.product_id.id)])
                        while finished_lot_id:
                            increment += 1
                            lot_name = sale_lot.name + str(increment).zfill(int(numbers_to_add))
                            finished_lot_id = self.env['stock.production.lot'].search([('name', '=', lot_name), ('product_id', '=', self.product_id.id)])
                    if not finished_lot_id:
                        finished_lot_id = self.env['stock.production.lot'].create({
                            'name': lot_name,
                            'product_id': production.product_id.id,
                            'company_id': production.company_id.id
                        })
                    res['finished_lot_id'] = finished_lot_id.id
        return res

    # serial_increment = fields.Integer(string='Serial Increment')

    # def continue_production(self):
    #     """ Overridden Method
    #         Save current wizard and directly opens a new after updating serial increment
    #     """
    #     self.ensure_one()
    #     res = super(MrpProductProduce, self).continue_production()
    #     if self.product_tracking == 'serial':
    #         res['context'].update({'default_serial_increment': self.serial_increment + 1})
    #     return res
