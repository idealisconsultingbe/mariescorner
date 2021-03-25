# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BatchPickingImportWizard(models.TransientModel):
    _name = 'stock.picking.batch.import.wizard'
    _description = 'Batch Picking Import Wizard'

    text_file = fields.Binary(string='File', required=True)
    batch_picking_id = fields.Many2one('stock.picking.batch', string='Batch Picking', required=True)
    batch_picking_import_line_ids = fields.One2many('stock.picking.batch.import.line', 'batch_picking_import_id', string='Batch Picking Import Lines')

    @api.onchange('text_file')
    def _onchange_text_file(self):
        if self.text_file:
            file_lines = self._strings_from_binary_txt_file(self.text_file)
            lot_names = self.batch_picking_id.mapped('move_line_ids.lot_name')
            list_line_values = []
            for line in file_lines:
                if line in lot_names:
                    move_lines = self.batch_picking_id.move_line_ids.filtered(lambda ml: ml.lot_name == line)
                    list_line_values += [(0, 0, {'lot_name': line, 'move_line_ids': move_lines.ids})]
                else:
                    list_line_values += [(0, 0, {'lot_name': line})]
            self.batch_picking_import_line_ids = list_line_values

    def import_file_action(self):
        self.ensure_one()
        if self.text_file:
            file_lines = self._strings_from_binary_txt_file(self.text_file)
            lot_names = self.batch_picking_id.mapped('move_line_ids.lot_name')
            for line in file_lines:
                if line in lot_names:
                    move_lines = self.batch_picking_id.move_line_ids.filtered(lambda ml: ml.lot_name == line)
                    move_lines.qty_done = 1.0

    def _strings_from_binary_txt_file(self, binary):
        if not binary:
            return False
        file_content = base64.decodestring(binary)
        try:
            file_content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            raise UserError(_('Only unicode text files (.txt) are allowed.'))
        return file_content.split('\r\n')

class BatchPickingImportLine(models.TransientModel):
    _name = 'stock.picking.batch.import.line'
    _description = 'Batch Picking Import Line'

    batch_picking_import_id = fields.Many2one('stock.picking.batch.import.wizard', string='Batch Picking Import Wizard')
    lot_name = fields.Char(string='Lot Name')
    move_line_ids = fields.Many2many('stock.move.line', string='Detailed Operations')
