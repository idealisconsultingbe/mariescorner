# -*- coding: utf-8 -*-
# Part of Idealis. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountIncoterms(models.Model):
    _inherit = 'account.incoterms'

    code = fields.Char(size=32)
