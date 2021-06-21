# -*- coding: utf-8 -*-
# Part of Idealis. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    short_name = fields.Text(string='Description', related='lot_id.short_name')
