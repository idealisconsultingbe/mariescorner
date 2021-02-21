# -*- coding: utf-8 -*-
"""
Configure default code for every product belonging to a specific category.
"""

import argparse
import logging


parser = argparse.ArgumentParser(description="")
parser.add_argument('database')
parser.add_argument('product_category_id')
args = parser.parse_args()

session.open(db=args.database)

logging.info('Load product category.')
product_category = session.env['product.category'].search([('id', 'child_of', int(args.product_category_id))])
logging.info('Product category loaded %s.' % product_category.mapped('name'))

logging.info('Load product variants.')
products = session.env['product.product'].search([('categ_id', 'in', product_category.ids)])
logging.info('%s Product variants loaded.' % len(products.ids))

logging.info('Start configuring default code.')
for product in products:
    default_code = ""
    if product.product_template_attribute_value_ids: # and not product.default_code:
        for pt_attribute in product.product_template_attribute_value_ids:
            default_code = "{}/{}".format(default_code, pt_attribute.product_attribute_value_id.name) if default_code else pt_attribute.product_attribute_value_id.name
        product.write({'default_code': default_code})
session.cr.commit()
logging.info('Product variants default code configured')

session.cr.commit()
session.close()
logging.info('Done')

