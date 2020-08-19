# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero


class Picking(models.Model):
    _inherit = 'stock.picking'

    update_lot_name_visible = fields.Boolean(string='Button Update Lot Name Visibility', compute='_compute_update_lot_name_visible')

    @api.depends('move_lines.sales_lot_id')
    def _compute_update_lot_name_visible(self):
        """ Compute lot name visibility """
        for picking in self:
            picking.update_lot_name_visible = False
            if any(move_line.sales_lot_id for move_line in picking.move_lines):
                picking.update_lot_name_visible = True

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
            serial_numbers_to_add = self.env['ir.config_parameter'].sudo().get_param('mc_sales_lot.additional_serial_number')
            if not self.move_line_ids:
                precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                # select only moves in correct state with a quantity set and no Sales Lot
                for move_line in self.move_lines.filtered(
                        lambda m: m.state not in ('done', 'cancel') and m.product_uom_qty and m.sales_lot_id):
                    product = move_line.product_id
                    if product and product.tracking != 'none' and float_is_zero(move_line.quantity_done, precision_digits=precision_digits):
                        if product.tracking == 'lot':
                            # Lots should use Sales Lot name
                            self.env['stock.move.line'].create(move_line._prepare_move_line_vals(lot_name=move_line.sales_lot_id.name, quantity=move_line.product_uom_qty))
                        else:
                            # Serial numbers should use Sales Lot name + 'extra numbers' with increment
                            lot_name = move_line.sales_lot_id.name + str(self.serial_increment).zfill(serial_numbers_to_add)
                            self.env['stock.move.line'].create(move_line._prepare_move_line_vals(lot_name=lot_name, quantity=move_line.product_uom_qty))
                            self.serial_increment += 1
            else:
                # if there are already move lines, update them
                serial_increment = 1
                for line in self.move_line_ids.filtered(lambda m: m.sales_lot_id):
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_id:
                            if product.tracking == 'lot':
                                line.update({'lot_name': line.sales_lot_id.name})
                            else:
                                lot_name = line.sales_lot_id.name + str(serial_increment).zfill(int(serial_numbers_to_add))
                                line.update({'lot_name': lot_name})
                                serial_increment += 1
