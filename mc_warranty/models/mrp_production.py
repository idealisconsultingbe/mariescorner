# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mc_care = fields.Boolean(related='sales_lot_id.mc_care', string='Mc Care', store=True)
