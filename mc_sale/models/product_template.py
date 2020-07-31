# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tailor_made = fields.Boolean('Is Tailor Made')
