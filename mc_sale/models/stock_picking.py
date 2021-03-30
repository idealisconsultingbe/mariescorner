# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    carrier_id = fields.Many2one('delivery.carrier', tracking=True)
    carrier_tracking_ref = fields.Char(tracking=True)