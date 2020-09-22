# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'
    
    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        """
        Overwrite the standard method.
        Since because of our custom development bom line could not have a product_id we have to adapt this method.
        """
        components = []
        total = 0
        for line in bom.bom_line_ids:
            line_product = line.product_id or line.product_tmpl_id # Custom changes instead of using everywhere line.product_id we use the line.product_tmpl_id if no product_id is found.
            line_product_tmpl = line_product if line_product._name == 'product.template' else line_product.product_tmpl_id
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            company = bom.company_id or self.env.company
            if line_product == line_product_tmpl and line_product.product_variant_ids:
                product_tmpl = line_product.with_context(force_company=company.id)
                average_standard_price = sum(product_tmpl.product_variant_ids.mapped('standard_price'))/len(product_tmpl.product_variant_ids)
                price = line_product.uom_id._compute_price(average_standard_price, line.product_uom_id) * line_quantity
            else:
                price = line_product.uom_id._compute_price(line_product.with_context(force_company=company.id).standard_price, line.product_uom_id) * line_quantity
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(line_quantity, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = self._get_price(line.child_bom_id, factor, line_product)
            else:
                sub_total = price
            sub_total = self.env.company.currency_id.round(sub_total)
            components.append({
                'prod_id': line_product.id,
                'prod_name': line_product.display_name,
                'code': line.child_bom_id and line.child_bom_id.display_name or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_cost': company.currency_id.round(price),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'total': sub_total,
                'child_bom': line.child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'attachments': self.env['mrp.document'].search(['|', '&',
                    ('res_model', '=', 'product.product'), ('res_id', '=', line_product.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', line_product_tmpl.id)]),

            })
            total += sub_total
        return components, total
    
    def _get_price(self, bom, factor, product):
        """
        Overwrite the standard method.
        Since because of our custom development bom line could not have a product_id we have to adapt this method.
        """
        price = 0
        if bom.routing_id:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(bom.routing_id, operation_cycle, 0)
            price += sum([op['total'] for op in operations])

        for line in bom.bom_line_ids:
            line_product = line.product_id or line.product_tmpl_id # Custom changes instead of using everywhere line.product_id we use the line.product_tmpl_id if no product_id is found.
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(line.product_qty * factor, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_price = self._get_price(line.child_bom_id, qty, line_product)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor
                company = bom.company_id or self.env.company
                not_rounded_price = line_product.uom_id._compute_price(line_product.with_context(force_company=company.id).standard_price, line.product_uom_id) * prod_qty
                price += company.currency_id.round(not_rounded_price)
        return price

    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False):
        """
        Overwrite the standard method.
        Since because of our custom development bom line could not have a product_id we have to adapt this method.
        """

        def get_sub_lines(bom, product_id, line_qty, line_id, level):
            data = self._get_bom(bom_id=bom.id, product_id=product_id.id, line_qty=line_qty, line_id=line_id,
                                 level=level)
            bom_lines = data['components']
            lines = []
            for bom_line in bom_lines:
                lines.append({
                    'name': bom_line['prod_name'],
                    'type': 'bom',
                    'quantity': bom_line['prod_qty'],
                    'uom': bom_line['prod_uom'],
                    'prod_cost': bom_line['prod_cost'],
                    'bom_cost': bom_line['total'],
                    'level': bom_line['level'],
                    'code': bom_line['code'],
                    'child_bom': bom_line['child_bom'],
                    'prod_id': bom_line['prod_id']
                })
                if bom_line['child_bom'] and (unfolded or bom_line['child_bom'] in child_bom_ids):
                    line = self.env['mrp.bom.line'].browse(bom_line['line_id'])
                    line_product = line.product_id or line.product_tmpl_id # Custom changes instead of using everywhere line.product_id we use the line.product_tmpl_id if no product_id is found.
                    lines += (get_sub_lines(line.child_bom_id, line_product, bom_line['prod_qty'], line, level + 1))
            if data['operations']:
                lines.append({
                    'name': _('Operations'),
                    'type': 'operation',
                    'quantity': data['operations_time'],
                    'uom': _('minutes'),
                    'bom_cost': data['operations_cost'],
                    'level': level,
                })
                for operation in data['operations']:
                    if unfolded or 'operation-' + str(bom.id) in child_bom_ids:
                        lines.append({
                            'name': operation['name'],
                            'type': 'operation',
                            'quantity': operation['duration_expected'],
                            'uom': _('minutes'),
                            'bom_cost': operation['total'],
                            'level': level + 1,
                        })
            return lines

        bom = self.env['mrp.bom'].browse(bom_id)
        product = product_id or bom.product_id or bom.product_tmpl_id.product_variant_id
        data = self._get_bom(bom_id=bom_id, product_id=product.id, line_qty=qty)
        pdf_lines = get_sub_lines(bom, product, qty, False, 1)
        data['components'] = []
        data['lines'] = pdf_lines
        return data
