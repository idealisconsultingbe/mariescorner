# -*- coding: utf-8 -*-
# Part of Idealis. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class UoM(models.Model):
    _inherit = 'uom.uom'

    packaging_ratio = fields.Integer(string='Packaging Ratio', default=-1, help="Ratio used to compute quantity required in that unit of measure to fill a package:\n"
                                                                                "* -1: always 1 pack no matter product quantity\n"
                                                                                "* 0: this uom is not packed\n"
                                                                                "* [1,n]: one pack per n unit")
