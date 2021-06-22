# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_transport = fields.Boolean('Transport Fees Account', default=False)
