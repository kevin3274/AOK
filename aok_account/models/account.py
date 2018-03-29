# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    discount_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Discount Account', ondelete='restrict')


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    one_due_amount = fields.Boolean('Create one due amount', default=True)
