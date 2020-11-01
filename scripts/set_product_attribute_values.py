# -*- coding: utf-8 -*-
"""
Configure attributes-values for every product belonging to a specific category.
"""

import argparse
import logging


def add_missing_values(product_template_attribute, attribute_values):
    missing_values = attribute_values - product_template_attribute.value_ids
    if missing_values:
        product_template_attribute.write({'value_ids': [(4, id) for id in missing_values.ids]})


parser = argparse.ArgumentParser(description="")
parser.add_argument('database')
parser.add_argument('product_category_id')
parser.add_argument('product_attribute_ids')
args = parser.parse_args()

session.open(db=args.database)

logging.info('Load product category.')
product_category = session.env['product.category'].search([('id', 'child_of', int(args.product_category_id))])
logging.info('Product category loaded %s.' % product_category.mapped('name'))

logging.info('Load product templates.')
products = session.env['product.template'].search([('categ_id', 'in', product_category.ids)])
logging.info('%s Product templates loaded.' % len(products.ids))

product_attribute_ids = [int(id) for id in args.product_attribute_ids.split(',')]
logging.info('Load product attributes.')
attributes = session.env['product.attribute'].search([('id', 'in', product_attribute_ids)])
logging.info('%s Product attributes loaded.' % len(attributes.ids))

attribute_values_to_create = []
logging.info('Start configuring attribute values.')
i = 0
for product in products:
    i += 1
    for attribute in attributes:
        product_template_attributes_candidate = product.attribute_line_ids.filtered(lambda a: a.attribute_id.id == attribute.id)
        if product_template_attributes_candidate:
            add_missing_values(product_template_attributes_candidate[0], attribute.value_ids)
        else:
            attribute_values_to_create.append({'product_tmpl_id': product.id, 'attribute_id': attribute.id, 'value_ids': [(6, 0, attribute.value_ids.ids)]})
    if i % 100 == 0:
        session.cr.commit()
        logging.info('%s product templates configured' % i)
logging.info('%s product templates configured' % i)
session.cr.commit()
logging.info('%s missing product template attribute lines to create.' % len(attribute_values_to_create))
batch_of_values = []
i = 0
for attribute_value in attribute_values_to_create:
    batch_of_values.append(attribute_value)
    i+=1
    if i % 1000 == 0:
        session.env['product.template.attribute.line'].create(batch_of_values)
        batch_of_values = []
        session.cr.commit()
        logging.info('%s product template attribute lines created' % i)
session.env['product.template.attribute.line'].create(batch_of_values)
logging.info('%s product template attribute lines created' % i)

session.cr.commit()
session.close()
logging.info('Done')

