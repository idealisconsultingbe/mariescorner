# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from math import ceil
from odoo import api, fields, models



class AccountMove(models.Model):
    _inherit = 'account.move'

    number_of_packages = fields.Integer(string='Number of Packages', compute='_compute_number_of_packages', store=True)
    manual_number_of_packages = fields.Integer(string='Manual Number of Packages')
    is_package_number_user_defined = fields.Boolean(string='User Defined Package Number', default=False)

    @api.depends('is_package_number_user_defined',
                 'manual_number_of_packages',
                 'invoice_line_ids',
                 'invoice_line_ids.quantity',
                 'invoice_line_ids.product_uom_id',
                 'invoice_line_ids.product_id',
                 'invoice_line_ids.product_uom_id.packaging_ratio',
                 'invoice_line_ids.product_id.categ_id.is_packed'
                 )
    def _compute_number_of_packages(self):
        """
        Compute the number of package of an invoice depending on the package ratio of the uom unit and the product categories.
        """
        for move in self:
            # The user has manually set a number of packages.
            if move.is_package_number_user_defined:
                move.number_of_packages = move.manual_number_of_packages
            else:
                nb_packages = 0
                for line in move.invoice_line_ids.filtered(lambda line: line.product_id.categ_id.is_packed if line.product_id else False):
                    # If ratio is equal to zero then number of package is always zero.
                    if line.product_uom_id.packaging_ratio == 0 or not line.product_uom_id.packaging_ratio:
                        continue
                    # If ratio is lower than zero then number of package is always one.
                    elif line.product_uom_id.packaging_ratio < 0:
                        nb_packages += 1
                    # If ratio is bigger than zero then number of package is quantity / ratio (with upper rounding).
                    else:
                        nb_packages += ceil(line.quantity / line.product_uom_id.packaging_ratio)
                move.number_of_packages = nb_packages

    def write(self, vals):
        """
        If we modify the short name in the invoice_line_ids add it to the corresponding line_ids
        The standard pop the 'invoice_line_ids' of the vals dictionary.
        :return:
        """
        if vals.get('line_ids') and vals.get('invoice_line_ids'):
            for invoice_line in vals['invoice_line_ids']:
                if len(invoice_line) == 3 and invoice_line[2] and 'short_name' in invoice_line[2]:
                    id = invoice_line[1]
                    for line in vals['line_ids']:
                        if len(line) == 3 and line[1] == id:
                            if isinstance(line[2], dict):
                                line[2]['short_name'] = invoice_line[2]['short_name']
                            else:
                                line[2] = {'short_name': invoice_line[2]['short_name']}
        res = super(AccountMove, self).write(vals)
        return res
