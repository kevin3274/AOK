# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'AOK Account',
    'category': 'Accounting',
    'sequence': 60,
    'summary': 'AOK Account',
    'description': "",
    'website': 'https://www.odoo.com/',
    'depends': ['account_accountant', 'account_banking_sepa_credit_transfer'],
    'data': [
        'views/account_views.xml',
        'views/partner_views.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
