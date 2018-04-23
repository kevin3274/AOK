# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
from datetime import datetime

from odoo import api, fields, models, _


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    is_full_amount = fields.Boolean(string="Full Amount Deprecation", default=True)
    asset_sequence = fields.Char(string="Sequence", readonly=True, states={'draft': [('readonly', False)]}, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('account.asset.asset'))
    location = fields.Char()
    quantity = fields.Float(default="1.0")
    leave_date = fields.Date(string='Date Leave', readonly=True)

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.is_full_amount = self.category_id.is_full_amount

    @api.multi
    def set_to_close(self):
        self.write({'leave_date': datetime.today()})
        return super(AccountAssetAsset, self).set_to_close()

    def _compute_board_amount(self, sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date):
        amount = 0
        if sequence == undone_dotation_number:
            amount = residual_amount
        else:
            if self.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                amount = round(amount) if self.is_full_amount else amount
                if self.prorata:
                    amount = amount_to_depr / self.method_number
                    amount = round(amount) if self.is_full_amount else amount
                    if sequence == 1:
                        if self.method_period % 12 != 0:
                            date = datetime.strptime(self.date, '%Y-%m-%d')
                            month_days = calendar.monthrange(date.year, date.month)[1]
                            days = month_days - date.day + 1
                            amount = (amount_to_depr / self.method_number) / month_days * days
                            amount = round(amount) if self.is_full_amount else amount
                        else:
                            days = (self.company_id.compute_fiscalyear_dates(depreciation_date)['date_to'] - depreciation_date).days + 1
                            amount = (amount_to_depr / self.method_number) / total_days * days
                            amount = round(amount) if self.is_full_amount else amount
            elif self.method == 'degressive':
                amount = residual_amount * self.method_progress_factor
                amount = round(amount) if self.is_full_amount else amount
                if self.prorata:
                    if sequence == 1:
                        if self.method_period % 12 != 0:
                            date = datetime.strptime(self.date, '%Y-%m-%d')
                            month_days = calendar.monthrange(date.year, date.month)[1]
                            days = month_days - date.day + 1
                            amount = (residual_amount * self.method_progress_factor) / month_days * days
                            amount = round(amount) if self.is_full_amount else amount
                        else:
                            days = (self.company_id.compute_fiscalyear_dates(depreciation_date)['date_to'] - depreciation_date).days + 1
                            amount = (residual_amount * self.method_progress_factor) / total_days * days
                            amount = round(amount) if self.is_full_amount else amount
        return amount


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    is_full_amount = fields.Boolean(string="Full Amount Deprecation", default=True)


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def post_lines_and_close_asset(self):
        # we re-evaluate the assets to determine whether we can close them
        if self.env.context.get('from_button'):
            for line in self:
                line.log_message_when_posted()
                asset = line.asset_id
                if asset.currency_id.is_zero(asset.value_residual):
                    asset.message_post(body=_("Document closed."))
                    asset.write({'state': 'close'})
