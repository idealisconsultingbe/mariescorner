# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    send_mail_order_confirmation = fields.Boolean(string='Send order confirmation mail')
    is_packed = fields.Boolean(string='Is Packed', default=True, help='Check this box if products of this category are packed for delivery by default.')
