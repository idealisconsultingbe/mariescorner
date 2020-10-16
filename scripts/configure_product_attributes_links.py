# -*- coding: utf-8 -*-
"""
Link attributes-values between them-selves.
"""

import argparse
import logging


def get_linked_values(attribute, value_name):
    attribute_values = session.env['product.attribute.value']
    for att in attribute.product_attribute_ids:
        value = att.value_ids.filtered(lambda v: v.name == value_name)
        if not value:
            value = session.env['product.attribute.value'].create({'attribute_id': att.id, 'name': value_name})
        attribute_values |= value[0]
    return attribute_values


parser = argparse.ArgumentParser(description="")
parser.add_argument('database')
parser.add_argument('product_attribute_ids')
args = parser.parse_args()

session.open(db=args.database)

product_attribute_ids = [int(id) for id in args.product_attribute_ids.split(',')]
logging.info('Load product attributes.')
attributes = session.env['product.attribute'].search([('id', 'in', product_attribute_ids)])
logging.info('Product attributes loaded #%s.' % len(attributes.ids))

for attribute in attributes:
    for value in attribute.value_ids:
        linked_values_candidate = get_linked_values(attribute, value.name)
        missing_linked_values = linked_values_candidate - value.product_attribute_value_ids
        if missing_linked_values:
            value.write({'product_attribute_value_ids': [(4, id) for id in missing_linked_values.ids]})


session.cr.commit()
session.close()
logging.info('Done')

