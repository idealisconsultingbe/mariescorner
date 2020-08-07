# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.tools.float_utils import float_is_zero


class Picking(models.Model):
    _inherit = 'stock.picking'

    serial_increment = fields.Integer(string='Serial Increment', default=1)

    def button_update_lot_name(self):
        """
            Update Sales Lot names of current receipt.
            There are 2 possibles cases:
                -   if there are already move lines linked to this picking,
                    add Sales Lot name to each line in order to create a Stock Production Lot with this name
                -   if there are no move lines, create them with Sales Lot names in their values
        """
        self.ensure_one()
        # this should work only for receipt
        if self.picking_type_code == 'incoming':
            # retrieve 'extra numbers' to add to serial numbers from configuration parameters
            serial_numbers_to_add = self.env['ir.config_parameter'].sudo().get_param('mc_sale.additional_serial_number')
            if not self.move_line_ids:
                precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                # select only moves in correct state with a quantity set and no Sales Lot
                for move_line in self.move_lines.filtered(
                        lambda m: m.state not in ('done', 'cancel') and m.product_uom_qty and m.sales_lot_id):
                    product = move_line.product_id
                    if product and product.tracking != 'none' and float_is_zero(move_line.quantity_done, precision_digits=precision_digits):
                        if product.tracking == 'lot':
                            # Lots should use Sales Lot name
                            self.env['stock.move.line'].create(self._get_move_line_vals(move_line, move_line.sales_lot_id.name))
                        else:
                            # Serial numbers should use Sales Lot name + 'extra numbers' with increment
                            lot_name = move_line.sales_lot_id.name + str(self.serial_increment).zfill(serial_numbers_to_add)
                            self.env['stock.move.line'].create(self._get_move_line_vals(move_line, lot_name))
                            self.serial_increment += 1
            else:
                # if there are already move lines, update them
                for line in self.move_line_ids.filtered(lambda m: m.sales_lot_id):
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            if product.tracking == 'lot':
                                line.update({'lot_name': line.sales_lot_id.name})
                            else:
                                lot_name = line.sales_lot_id.name + str(self.serial_increment).zfill(int(serial_numbers_to_add))
                                line.update({'lot_name': lot_name})
                                self.serial_increment += 1

    def _get_move_line_vals(self, move, lot_name):
        return {
                'picking_id': move.picking_id.id,
                'lot_name': lot_name,
                'qty_done': move.product_uom_qty,
                'move_id': move.id,
                'product_id': move.product_id.id,
                'product_uom_id': move.product_uom.id,
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
                'company_id': move.company_id.id
            }
