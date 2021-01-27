# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _


def get_fabrics_lot_details(productions):
    productions_fabric_lots = {}
    for production in productions:
        lots = {}
        for move_line in production.move_raw_ids.mapped('move_line_ids').filtered(
                lambda move_line: move_line.product_id.is_fabric):
            if move_line.lot_id and move_line.lot_id.name not in lots:
                lots[move_line.lot_id.name] = {
                    'product': production.product_id,
                    'manuf_num': production.sales_lot_id,
                    'qty': production.product_qty,
                    'total_fabric': move_line.qty_done,
                    'fabric': move_line.product_id,
                    'fabric_uom': move_line.product_uom_id.name,
                    'finished_product': move_line.lot_produced_ids,
                }
            elif move_line.lot_id:
                lots[move_line.lot_id.name]['total_fabric'] += move_line.qty_done
                lots[move_line.lot_id.name]['finished_product'] |= move_line.lot_produced_ids
        for lot in lots:
            lots[lot]['unit_fabric'] = lots[lot]['total_fabric'] / len(lots[lot]['finished_product']) or 1
        productions_fabric_lots[production.id] = lots
    return productions_fabric_lots


class ManufacturingReport(models.Model):
    _name = 'report.mc_sales_lot.report_mrp_saleslot'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_sales_lot.report_mrp_saleslot')
        productions = self.env[report.model].browse(docids)
        productions_fabric_lots = get_fabrics_lot_details(productions)
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': productions,
            'data': data,
            'fabrics_lots': productions_fabric_lots,
        }


class SalesLotReport(models.Model):
    _inherit = 'report.mc_sales_lot.report_saleslot'

    def _get_report_values(self, docids, data=None):
        values = super(SalesLotReport, self)._get_report_values(docids, data)
        sales_lot = values['docs']
        productions = sales_lot.mapped('production_ids')
        productions_fabric_lots = get_fabrics_lot_details(productions)
        values.update({'fabrics_lots': productions_fabric_lots,})
        return values
