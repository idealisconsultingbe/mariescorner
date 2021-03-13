# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('ref')
    def _check_unique_ref(self):
        for partner in self:
            result = self.search([('id', '!=', partner.id), ('ref', '!=', ""), ('ref', '=', partner.ref)], limit=1)
            if result:
                message = _('You have already a partner ({}) with this reference ({})'.format(result.name, partner.ref))
                raise ValidationError(message)

    @api.model_create_multi
    def create(self, vals):
        """
        Overridden method
        Use a sequence to fill partner ref if field is not set
        """
        for contact_vals in vals:
            if not contact_vals.get('ref', False):
                sequence = self.env['ir.sequence'].next_by_code('res.partner')
                contact_vals.update({'ref': sequence})
        return super(ResPartner, self).create(vals)
