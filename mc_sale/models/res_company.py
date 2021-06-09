# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    eori = fields.Char(string='EORI')
    eori_uk = fields.Char(string='EORI UK')
