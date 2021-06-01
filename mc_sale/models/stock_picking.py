# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    destination_usage = fields.Selection(related='picking_type_id.default_location_dest_id.usage', string='Destination Location Type', help="Technical field used in view", readonly=True)

    # changes to existing fields
    carrier_id = fields.Many2one('delivery.carrier', tracking=True)
    carrier_tracking_ref = fields.Char(tracking=True)
    scheduled_date = fields.Datetime(states={'cancel': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', states={'cancel': [('readonly', True)]}, tracking=True)

    def _set_scheduled_date(self):
        return super(StockPicking, self.filtered(lambda record: record.state != 'done'))._set_scheduled_date()
