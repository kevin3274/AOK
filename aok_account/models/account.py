# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    discount_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Discount Account', ondelete='restrict')


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    one_due_amount = fields.Boolean('Create one due amount', default=True)

    @api.one
    def compute(self, value, date_ref=False):
        date_ref = date_ref or fields.Date.today()
        amount = value
        sign = value < 0 and -1 or 1
        result = []
        if self.env.context.get('currency_id'):
            currency = self.env['res.currency'].browse(self.env.context['currency_id'])
        else:
            currency = self.env.user.company_id.currency_id
        for line in self.line_ids:
            if line.value == 'fixed':
                amt = sign * currency.round(line.value_amount)
            elif line.value == 'percent':
                amt = currency.round(value * (line.value_amount / 100.0))
            elif line.value == 'balance':
                amt = currency.round(amount)
            if amt:
                next_date = fields.Date.from_string(date_ref)
                if line.option == 'day_after_invoice_date':
                    next_date += relativedelta(days=line.days)
                elif line.option == 'fix_day_following_month':
                    next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                    next_date = next_first_date + relativedelta(days=line.days - 1)
                elif line.option == 'last_day_following_month':
                    next_date += relativedelta(day=31, months=1)  # Getting last day of next month
                elif line.option == 'last_day_current_month':
                    next_date += relativedelta(day=31, months=0)  # Getting last day of next month
                result.append((fields.Date.to_string(next_date), amt))
                amount -= amt
        amount = sum(amt for _, amt in result)
        dist = currency.round(value - amount)
        if dist:
            last_date = result and result[-1][0] or fields.Date.today()
            result.append((last_date, dist))
        if self.one_due_amount:
            return [(result[-1][0], value)]
        return result

    @api.one
    def compute_payment_term_date(self, value, date_ref=False):
        date_ref = date_ref or fields.Date.today()
        amount = value
        sign = value < 0 and -1 or 1
        result = []
        if self.env.context.get('currency_id'):
            currency = self.env['res.currency'].browse(self.env.context['currency_id'])
        else:
            currency = self.env.user.company_id.currency_id
        for line in self.line_ids.sorted():
            if line.value == 'fixed':
                amt = sign * currency.round(line.value_amount)
            elif line.value == 'percent':
                amt = currency.round(value * (line.value_amount / 100.0))
            elif line.value == 'balance':
                amt = currency.round(amount)
            if amt:
                next_date = fields.Date.from_string(date_ref)
                if line.option == 'day_after_invoice_date':
                    next_date += relativedelta(days=line.days)
                elif line.option == 'fix_day_following_month':
                    next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                    next_date = next_first_date + relativedelta(days=line.days - 1)
                elif line.option == 'last_day_following_month':
                    next_date += relativedelta(day=31, months=1)  # Getting last day of next month
                elif line.option == 'last_day_current_month':
                    next_date += relativedelta(day=31, months=0)  # Getting last day of next month
                result.append((fields.Date.to_string(next_date), amt, line))
                amount -= amt
        amount = sum(amt for _, amt, _ in result)
        dist = currency.round(value - amount)
        if dist:
            last_date = result and result[-1][0] or fields.Date.today()
            result.append((last_date, dist, line))
#         if self.one_due_amount:
#             return [(result[-1][0], value, line)]
        return result


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    consider_payment_discount = fields.Boolean("Consider Payment Discount", default=True)


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    payment_line_discount_ids = fields.One2many('account.payment.line.discount', 'payment_line_id', string="Payment Order Line Discount")
    payment_discount = fields.Monetary(string="Payment Discount", currency_field='currency_id')
    deduct_discount = fields.Boolean("Deduct Discount")
    discount_due_date = fields.Date(string="Discount Due Date")


class AccountPaymentLineDiscount(models.Model):
    _name = 'account.payment.line.discount'
    _description = 'Payment Line Discount'

    def _compute_all(self):
        for record in self:
            invoice = record.payment_line_id.move_line_id.invoice_id
            record.invoice_amount = record.invoice_tax_id.base + record.invoice_tax_id.amount_total

            date_invoice = invoice.date_invoice
            if not date_invoice:
                date_invoice = fields.Date.context_today(self)

            pterm = invoice.payment_term_id
            pterm_list = pterm.with_context(currency_id=invoice.company_id.currency_id.id).compute_payment_term_date(value=record.invoice_amount, date_ref=date_invoice)[0]
            discount_date = payment_discount = False
            payment_discount_amount = 0.0
            for line in pterm_list:
                if line[2].value == 'percent' and fields.Date.from_string(line[0]) >= fields.Date.from_string(fields.Date.context_today(self)):
                    discount_date = line[0]
                    payment_discount = line[2].value_amount
                    payment_discount_amount = line[1]
                    break
            record.discount_due_date = discount_date
            record.payment_discount_perc = payment_discount
            record.payment_discount = payment_discount_amount

    payment_line_id = fields.Many2one("account.payment.line", string="Payment Line")
    currency_id = fields.Many2one(
        'res.currency', string='Currency of the Payment Transaction',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    invoice_amount = fields.Monetary(compute="_compute_all", string="Invoice Amount", currency_field='currency_id')
    discount_due_date = fields.Date(compute="_compute_all", string="Discount Due Date")
    payment_discount_perc = fields.Float(compute="_compute_all", string="Payment Discount %")
    payment_discount = fields.Monetary(compute="_compute_all", string="Payment Discount", currency_field='currency_id')
    tax_id = fields.Many2one("account.tax", string="Tax")
    account_id = fields.Many2one("account.account", string="Account")
    invoice_tax_id = fields.Many2one('account.invoice.tax', string="Account Invoice Tax")


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    consider_payment_discount = fields.Boolean(related="payment_mode_id.consider_payment_discount", string="Consider Payment Discount")

    @api.multi
    def draft2open(self):
        AccountPaymentLineDiscount = self.env['account.payment.line.discount']
        AccountInvoiceTax = self.env['account.invoice.tax']
        for order in self:
            for line in order.payment_line_ids:
                if line.move_line_id:
                    invoice = line.move_line_id.invoice_id
                    for tax_line in invoice.tax_line_ids:
                        AccountPaymentLineDiscount.create({'payment_line_id': line.id, 'tax_id': tax_line.tax_id.id, 'account_id': tax_line.tax_id.discount_account_id.id, 'invoice_tax_id': tax_line.id})
        return super(AccountPaymentOrder, self).draft2open()
