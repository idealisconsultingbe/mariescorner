# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
   
    current_revision_id = fields.Many2one('sale.order', 'Current revision', readonly=True, copy=True)
    old_revision_ids = fields.One2many('sale.order', 'current_revision_id', 'Old revisions', readonly=True, context={'active_test': False})
    revision_number = fields.Integer('Revision', copy=False)
    active = fields.Boolean('Active', default=True, copy=True)
    
    def action_revision(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        rev = self.with_context(sale_revision_history=True).copy()
        (self | self.old_revision_ids).write({'current_revision_id': rev.id})
        self.action_cancel()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': rev.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
        
    @api.returns('self', lambda value: value.id)
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('sale_revision_history'):
            prev_name = self.name
            revno = self.revision_number + 1
            self.write({'revision_number': revno,'name': '%s-%02d' % (self.name, revno + 1)})
            defaults.update({'name': prev_name,
                             'revision_number': revno,
                             'active': True,})
        return super(SaleOrder, self).copy(defaults)
