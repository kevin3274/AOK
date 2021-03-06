# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from datetime import datetime
from odoo.tools.misc import xlwt
from io import BytesIO

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssetSummaryReport(models.TransientModel):
    _name = 'asset.summary.report'
    _description = 'Asset Summary Report'

    name = fields.Char("File Name")
    date_to = fields.Date(string='Date To', required=True, default=lambda *a: datetime.today())
    date_from = fields.Date(string='Date From', required=True, default=lambda *a: datetime.today())
    data = fields.Binary('File', readonly=True)

    @api.constrains('date_to', 'date_from')
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValidationError(_("'From Date' must be less than or equal to 'To Date' !"))

    @api.multi
    def print_report(self):
        records = self.env['account.asset.asset'].search([('state', '!=', 'draft'), ('date', '>=', self.date_from),
                                                      ('date', '<=', self.date_to)])
        prev_records = self.env['account.asset.asset'].search([('state', '!=', 'draft'), ('date', '<', self.date_from)])
        tot_records = records + prev_records
        if not tot_records:
            raise ValidationError(_('There are no record Found!'))
        accounts = records.mapped('category_id').mapped('account_asset_id')

        fieldss = ['', 'Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5', 'Column 6', 'Column 7', 'Column 8', 'Column 9']

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        raw = 0
        base_style = xlwt.easyxf('align: wrap yes')
        for field in fieldss:
            worksheet.write(0, raw, field, base_style)
            raw += 1
        col = 1
        for account in accounts:
            raw = 0
            for field in fieldss:
                if field == '':
                    worksheet.write(col, raw, account.name, base_style)
                elif field == 'Column 1':
                    value = sum(prev_records.filtered(lambda rec: rec.state == 'open').mapped('value'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Column 2':
                    value = sum(records.filtered(lambda rec: rec.state == 'open').mapped('value'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Column 3':
                    value = sum(records.filtered(lambda rec: rec.state == 'close').mapped('depreciation_line_ids').mapped('amount'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Column 4':
                    worksheet.write(col, raw, 0.0, base_style)
                elif field == 'Column 5':
                    depreciation_lines = prev_records.filtered(lambda rec: rec.state == 'open').mapped('depreciation_line_ids')
                    value = sum(depreciation_lines.filtered(lambda rec: rec.depreciation_date < self.date_from).mapped('amount'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Column 6':
                    depreciation_lines = records.filtered(lambda rec: rec.state == 'open').mapped('depreciation_line_ids')
                    value = sum(depreciation_lines.filtered(lambda rec: fields.Datetime.from_string(rec.depreciation_date).month == self.env.user.company_id.fiscalyear_last_month).mapped('remaining_value'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Column 7':
                    depreciation_lines = prev_records.filtered(lambda rec: rec.state == 'open').mapped('depreciation_line_ids')
                    value = sum(depreciation_lines.filtered(lambda rec: fields.Datetime.from_string(rec.depreciation_date).month == self.env.user.company_id.fiscalyear_last_month).mapped('remaining_value'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Column 8':
                    value = sum(records.filtered(lambda rec: rec.state == 'open').mapped('depreciation_line_ids').mapped('amount'))
                    worksheet.write(col, raw, value, base_style)
                elif field == 'Column 9':
                    worksheet.write(col, raw, 0.0, base_style)
                raw += 1
            col += 1
            fp = BytesIO()
            workbook.save(fp)
            fp.seek(0)
            data = base64.encodestring(fp.read())
            fp.close()
            name = "Asset_Summary_Report.xls"
            self.write({"name": name, 'data': data})
        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'asset.summary.report',
                'res_id': self.id,
                'view_id': self.env.ref('aok_account.view_asset_summary_report_download').id,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
