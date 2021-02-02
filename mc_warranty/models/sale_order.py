# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mc_care_warranty = fields.Boolean(string='Warranty Activated')
    final_partner_id = fields.Many2one('res.partner', string='Final Customer')
