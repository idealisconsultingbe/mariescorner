# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    category_type = fields.Selection([('chair', 'Chair'), ('2seats', 'Sofa 2 Seats'), ('3seats', 'Sofa 3 Seats'), ('other', 'Other')], string="Furniture Type")
