# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    inter_company_lot_id = fields.Many2one('stock.production.lot', string='InterCompany Production Lot')