# -*- coding: utf-8 -*-
"""
Create bom for product.template
"""

import argparse
import logging


def prepare_raw_mat_values():
    return [
        {'product_id': 35843, 'product_tmpl_id': 42728, 'product_qty': 1},
        {'product_tmpl_id': 7, 'product_attribute_ids': [(6, 0, [2, 11])], 'product_qty': 5, 'product_uom_id': 8},
        {'product_tmpl_id': 7, 'product_attribute_ids': [(6, 0, [9, 16])], 'product_qty': 0, 'product_uom_id': 8},
        {'product_tmpl_id': 434, 'product_attribute_ids': [(6, 0, [4, 5])], 'product_qty': 4},
        {'product_id': 553, 'product_tmpl_id': 430, 'product_qty': 4},
        {'product_tmpl_id': 428, 'product_attribute_ids': [(6, 0, [23])], 'product_qty': 1},
        {'product_id': 554, 'product_tmpl_id': 431, 'product_qty': 1},
        {'product_id': 555, 'product_tmpl_id': 432, 'product_qty': 1.85},
        {'product_id': 556, 'product_tmpl_id': 433, 'product_qty': 3},
    ]


def prepare_bom_values(product):
    return {
        'product_tmpl_id': product.id,
        'product_qty': 1,
        'type': 'normal',
        'company_id': 2,
        'bom_line_ids': [(0, 0, raw_mat_values) for raw_mat_values in prepare_raw_mat_values()],
    }


parser = argparse.ArgumentParser(description="")
parser.add_argument('database')
parser.add_argument('product_category_id')
args = parser.parse_args()

session.open(db=args.database)

logging.info('Load product category.')
product_category = session.env['product.category'].search([('id', 'child_of', int(args.product_category_id))])
logging.info('Product category loaded %s.' % product_category.mapped('name'))

logging.info('Load product templates.')
products = session.env['product.template'].search([('categ_id', 'in', product_category.ids)])
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

