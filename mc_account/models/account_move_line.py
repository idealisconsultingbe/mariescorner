# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    origin = fields.Char(string='Source Document', help='Reference of the document that generated this invoice/bill.')
    partner_ref = fields.Char('Vendor/Customer Reference')
