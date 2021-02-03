# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _


class BatchPickingReport(models.Model):
    _name = 'report.mc_batch_picking.batch_packing_list_report_template'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_batch_picking.batch_packing_list_report_template')
        batch_pickings = self.env[report.model].browse(docids)
        batch_pickings_by_carrier = {}
        for batch in batch_pickings:
            pickings_by_carrier = {}
            for picking in batch.picking_ids:
                if picking.carrier_id and picking.carrier_id.name in pickings_by_carrier:
                    pickings_by_carrier[picking.carrier_id.name] |= picking
                elif picking.carrier_id:
                    pickings_by_carrier[picking.carrier_id.name] = picking
                else:
                    if 'Undefined' not in pickings_by_carrier:
                        pickings_by_carrier['Undefined'] = self.env['stock.picking']
                    pickings_by_carrier['Undefined'] |= picking
            batch_pickings_by_carrier[batch.id] = pickings_by_carrier
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': batch_pickings,
            'data': data,
            'batch_pickings_by_carrier': batch_pickings_by_carrier,
        }

class PickingShipmentReport(models.Model):
    _name = 'report.mc_batch_picking.batch_packing_list_document'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_batch_picking.batch_packing_list_document')
        pickings = self.env[report.model].browse(docids)
        pickings_by_carrier = {}
        for picking in pickings:
            if picking.carrier_id and picking.carrier_id.name in pickings_by_carrier:
                pickings_by_carrier[picking.carrier_id.name] |= picking
            elif picking.carrier_id:
                pickings_by_carrier[picking.carrier_id.name] = picking
            else:
                if 'Undefined' not in pickings_by_carrier:
                    pickings_by_carrier['Undefined'] = self.env['stock.picking']
                pickings_by_carrier['Undefined'] |= picking
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': pickings,
            'data': data,
            'pickings_by_carrier': pickings_by_carrier,
        }