# -*- coding: utf-8 -*-
"""
This script sanitizes a copy of a production database for the delivery
so it becomes safe to use in a test environment.

Run this script with bin/python_openerp as generated by buildout.

NEVER RUN THIS SCRIPT ON THE PRODUCTION DATABASE.
"""
import argparse
import psycopg2
from contextlib import closing
from odoo import api


parser = argparse.ArgumentParser(description="Update the database to set it safe for testing")
parser.add_argument('database')
parser.add_argument('user')
parser.add_argument('password')
args = parser.parse_args()


##############################################################################
# parameters
#

PASSWORD = "999"

##############################################################################


def sanitize_prod_copy(cr):
    # change the password for all users so people
    # do not connect to the test database by accident
    cr.execute("UPDATE res_users SET password=%s WHERE id=2""", (PASSWORD,))

    # disable outgoing mail servers
    cr.execute("UPDATE ir_mail_server SET smtp_host=smtp_host || '.disabled', active=FALSE")

    # disable incomming mail servers
    cr.execute("UPDATE fetchmail_server SET server=server || '.disabled', active=FALSE, state='draft'")

    # remove google analytics key
    cr.execute("UPDATE website SET google_analytics_key=NULL""")


param = "dbname=%s user=%s host='localhost' password=%s" % (args.database, args.user, args.password)
with closing(psycopg2.connect(param)) as conn:
    with closing(conn.cursor()) as cr:
        sanitize_prod_copy(cr)
    conn.commit()

session.open(db=args.database)
with api.Environment.manage():
    env = api.Environment(session.cr, 1, {})

    module = env['ir.module.module'].search([('name', 'like', 'website_no_crawler')])
    module.button_immediate_install()

    module = env['ir.module.module'].search([('name', 'like', 'website_environment_ribbon')])
    module.button_immediate_install()

print("done")

