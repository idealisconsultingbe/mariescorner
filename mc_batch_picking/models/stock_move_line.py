# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import float_compare


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    carrier_id = fields.Many2one('delivery.carrier', string='Carrier', related='picking_id.carrier_id')
    inter_company_move_line_id = fields.Many2one('stock.move.line', string='InterCompany Stock Move Line')
    inter_company_batch_picking_name = fields.Char(string='Received From Batch', compute='_get_intercompany_batch_name', compute_sudo=True)

    def _get_intercompany_batch_name(self):
        """
        Get inter company batch picking name.
        """
        for sml in self:
            batch_name = ''
            if sml.inter_company_move_line_id and sml.inter_company_move_line_id.picking_id and sml.inter_company_move_line_id.picking_id.batch_id:
                batch_name = sml.inter_company_move_line_id.picking_id.batch_id.name
            sml.inter_company_batch_picking_name = batch_name

    def _action_done(self):
        """
        Overridden method
        In case of inter company transfer, the goal is to create/update move lines in the opposite company
        when we validate lines in current company. That way, move lines already exist before processing reception, possibly in batch.

        Logic:
        If line is an outgoing move line and parent move is linked to an inter company transfer
        then try to find candidate move lines to update in related company or create new ones.
        """
        ml_to_delete = self.env['stock.move.line']
        for ml in self:
            qty_done_float_compared = float_compare(ml.qty_done, 0, precision_rounding=ml.product_uom_id.rounding)
            if qty_done_float_compared == 0:
                ml_to_delete |= ml
        super(StockMoveLine, self)._action_done()
        self = self.sudo()
        for line in (self - ml_to_delete):
            move = line.move_id
            if line in move._get_out_move_lines() and move.sale_line_id.inter_company_po_line_id:
                po_line = move.sale_line_id.inter_company_po_line_id
                po_line_moves = po_line.move_ids.filtered(lambda m: m.state in ['waiting', 'confirmed', 'draft', 'partially_available', 'assigned'] and m.sales_lot_id == move.sales_lot_id)
                if po_line_moves:
                    to_update = po_line_moves.move_line_ids.filtered(lambda ml: ml.product_uom_id == line.product_uom_id and
                                                                       ml.product_id == line.product_id and
                                                                       ml.state == 'assigned' and
                                                                       ml.product_qty == line.qty_done and
                                                                       ml.product_uom_qty == line.qty_done and
                                                                       ml.sales_lot_id == line.sales_lot_id and
                                                                       not ml.lot_id and
                                                                       not ml.lot_name and
                                                                       not ml.inter_company_move_line_id)
                    if to_update:
                        to_update[0].update({'lot_name': line.lot_id.name, 'inter_company_move_line_id': line.id})
                    else:
                        self.env['stock.move.line'].create({
                            'company_id': po_line_moves[0].company_id.id,
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom_id.id,
                            'move_id': po_line_moves[0].id,
                            'lot_name': line.lot_id.name,
                            'inter_company_move_line_id': line.id,
                            'location_id': po_line_moves[0].picking_id.location_id.id,
                            'location_dest_id': po_line_moves[0].picking_id.location_dest_id.id,
                            'picking_id': po_line_moves[0].picking_id.id,
                        })
            if line.inter_company_move_line_id and line.lot_id:
                line.lot_id.update({'inter_company_lot_id': line.inter_company_move_line_id.lot_id})
