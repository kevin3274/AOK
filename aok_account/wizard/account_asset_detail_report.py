# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from datetime import datetime
from odoo.tools.misc import xlwt
from io import BytesIO

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssetDetailReport(models.TransientModel):
    _name = 'asset.detail.report'
    _description = 'Asset Detail Report'

    name = fields.Char("File Name")
    data = fields.Binary('File', readonly=True)

    @api.multi
    def print_report(self):
        res = self.env.user.company_id.compute_fiscalyear_dates(datetime.today())
        date_from = fields.Datetime.to_string(res.get('date_from'))
        date_to = fields.Datetime.to_string(res.get('date_to'))

        records = self.env['account.asset.asset'].search([('state', '!=', 'draft'), ('date', '>=', date_from),
                                                      ('date', '<=', date_to)])
        prev_records = self.env['account.asset.asset'].search([('state', '!=', 'draft'), ('date', '<', date_from)])
        assets = records + prev_records
        if not assets:
            raise ValidationError(_('There are no record Found!'))
        # accounts = records.mapped('category_id').mapped('account_asset_id')

        fieldss = ['', 'Gross Value', 'Gross Value if new asset this year', 'Sold or Disposed this year', 'Plus/minus transfers(always 0.00)', 'Depreciation since start still last year', 'Residual end of this year', 'Residual still last year', 'Depreciation this year', 'Depreciation this year(always 0.00)']

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        raw = 0
        base_style = xlwt.easyxf('align: wrap yes')
        for field in fieldss:
            worksheet.write(0, raw, field, base_style)
            raw += 1
        col = 1
        for asset in assets:
            raw = 0
            for field in fieldss:
                if field == '':
                    worksheet.write(col, raw, asset.name, base_style)
                elif field == 'Gross Value':
                    value = sum(asset.filtered(lambda rec: rec.state == 'open' and rec.date < date_from).mapped('value'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Gross Value if new asset this year':
                    value = sum(asset.filtered(lambda rec: rec.state == 'open' and rec.date >= date_from and rec.date <= date_to).mapped('value'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Sold or Disposed this year':
                    value = sum(asset.filtered(lambda rec: rec.state == 'close' and rec.date >= date_from and rec.date <= date_to).mapped('depreciation_line_ids').mapped('amount'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Plus/minus transfers(always 0.00)':
                    worksheet.write(col, raw, 0.0, base_style)
                elif field == 'Depreciation since start still last year':
                    depreciation_lines = asset.filtered(lambda rec: rec.state == 'open' and rec.date < date_from).mapped('depreciation_line_ids')
                    value = sum(depreciation_lines.filtered(lambda rec: rec.depreciation_date < date_from).mapped('amount'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Residual end of this year':
                    depreciation_lines = asset.filtered(lambda rec: rec.state == 'open' and rec.date >= date_from and rec.date <= date_to).mapped('depreciation_line_ids')
                    value = sum(depreciation_lines.filtered(lambda rec: fields.Datetime.from_string(rec.depreciation_date).month == self.env.user.company_id.fiscalyear_last_month).mapped('remaining_value'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Residual still last year':
                    depreciation_lines = asset.filtered(lambda rec: rec.state == 'open' and rec.date < date_from).mapped('depreciation_line_ids')
                    value = sum(depreciation_lines.filtered(lambda rec: fields.Datetime.from_string(rec.depreciation_date).month == self.env.user.company_id.fiscalyear_last_month).mapped('remaining_value'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Depreciation this year':
                    value = sum(asset.filtered(lambda rec: rec.state == 'open' and rec.date >= date_from and rec.date <= date_to).mapped('depreciation_line_ids').mapped('amount'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Depreciation this year(always 0.00)':
                    worksheet.write(col, raw, 0.0, base_style)
                raw += 1
            col += 1
            fp = BytesIO()
            workbook.save(fp)
            fp.seek(0)
            data = base64.encodestring(fp.read())
            fp.close()
            name = "Asset_Detail_Report.xls"
            self.write({"name": name, 'data': data})
        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'asset.detail.report',
                'res_id': self.id,
                'view_id': self.env.ref('aok_account.view_asset_detail_report_download').id,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
