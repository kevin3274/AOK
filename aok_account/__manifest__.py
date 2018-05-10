# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'AOK Account',
    'category': 'Accounting',
    'sequence': 60,
    'summary': 'AOK Account',
    'description': "",
    'website': 'https://www.odoo.com/',
    'depends': ['account_accountant', 'account_banking_sepa_credit_transfer', 'project', 'account_analytic_default', 'account_asset'],
    'data': [
        'views/account_views.xml',
        'views/partner_views.xml',
        'views/project_views.xml',
        'data/account_asset_sequence.xml',
        'views/account_asset_views.xml',
        'views/company_views.xml',
        'wizard/account_asset_summary_report_view.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
