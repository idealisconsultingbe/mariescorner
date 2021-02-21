# -*- coding: utf-8 -*-
"""
Create bom for product.template
"""

import argparse
import logging


def prepare_raw_mat_values():
    return [
        {'product_tmpl_id': 14721, 'product_attribute_ids': [(6, 0, [65, 66])], 'product_qty': 1, 'product_uom_id': 8},
        {'product_tmpl_id': 14721, 'product_attribute_ids': [(6, 0, [67, 68])], 'product_qty': 0, 'product_uom_id': 8},
        {'product_tmpl_id': 15070, 'product_attribute_ids': [(6, 0, [69, 70])], 'product_qty': 4},
        {'product_tmpl_id': 22304, 'product_attribute_ids': [(6, 0, [75])], 'product_qty': 1},
        {'product_tmpl_id': 22305, 'product_attribute_ids': [(6, 0, [91])], 'product_qty': 1},
        {'product_tmpl_id': 22306, 'product_attribute_ids': [(6, 0, [79])], 'product_qty': 1},
        {'product_tmpl_id': 22314, 'product_attribute_ids': [(6, 0, [76])], 'product_qty': 1},
        {'product_tmpl_id': 22307, 'product_attribute_ids': [(6, 0, [78])], 'product_qty': 1},
        {'product_tmpl_id': 22308, 'product_attribute_ids': [(6, 0, [80])], 'product_qty': 1},
        {'product_tmpl_id': 22309, 'product_attribute_ids': [(6, 0, [81])], 'product_qty': 1},
        {'product_tmpl_id': 22310, 'product_attribute_ids': [(6, 0, [82])], 'product_qty': 1},
        {'product_tmpl_id': 22311, 'product_attribute_ids': [(6, 0, [83])], 'product_qty': 1},
        {'product_tmpl_id': 22312, 'product_attribute_ids': [(6, 0, [84])], 'product_qty': 1},
        {'product_tmpl_id': 22313, 'product_attribute_ids': [(6, 0, [85])], 'product_qty': 1},
    ]


def prepare_bom_values(product):
    return {
        'product_tmpl_id': product.id,
        'product_qty': 1,
        'type': 'normal',
        'company_id': 3,
        'bom_line_ids': [(0, 0, raw_mat_values) for raw_mat_values in prepare_raw_mat_values()],
    }


parser = argparse.ArgumentParser(description="")
parser.add_argument('database')
parser.add_argument('product_category_id')
parser.add_argument('seller_id')
args = parser.parse_args()

session.open(db=args.database)
seller_id = int(args.seller_id)

logging.info('Load product category.')
product_category = session.env['product.category'].search([('id', 'child_of', int(args.product_category_id))])
logging.info('Product category loaded %s.' % product_category.mapped('name'))

logging.info('Load product templates.')
products = session.env['product.template'].search([('categ_id', 'in', product_category.ids)])
products = products.filtered(lambda p: seller_id in p.seller_ids.mapped('name.id'))
logging.info('%s Product templates loaded.' % len(products.ids))

values = []
for product in products:
    existing_bom = session.env['mrp.bom'].search([('product_tmpl_id', '=', product.id)])
    if not existing_bom:
        values.append(prepare_bom_values(product))
session.env['mrp.bom'].create(values)

session.cr.commit()
session.close()
logging.info('Done')

