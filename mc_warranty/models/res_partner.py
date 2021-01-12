# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    final_customer = fields.Boolean(string='Is Final Customer')
    final_customer_sale_order_ids = fields.One2many('sale.order', 'final_partner_id', string='Final Customer Sales')

