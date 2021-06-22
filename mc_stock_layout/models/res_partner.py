# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    delivery_slip_default_receiver = fields.Boolean(string='Delivery Slip Receiver', default=False, help='If selected this sale representative is automatically set as receiver for the delivery slip')
