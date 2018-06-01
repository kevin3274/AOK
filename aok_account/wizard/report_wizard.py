# -*- coding: utf-8 -*-

import base64
import datetime
import xlsxwriter

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveReportService(models.TransientModel):
    _name = 'account.move.report.as.400'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    invoice_data = fields.Char('Name')
    file_name = fields.Binary('Invoice Report', readonly=True)

    def account_move_lines(self):
        move_line_ids = []
        if self.start_date > self.end_date:
            raise UserError("End date is greter than start date")
        else:
            move_line_ids = self.env[('account.move.line')].search([('date', '>=', self.start_date), ('date', '<=', self.end_date)])
        return move_line_ids

    def _write_list_data(self, worksheet, row, col, datas, format):
        for val in datas:
            worksheet.write(row, col, val, format)
            worksheet.set_column(row, col, 20)
            col += 1
        return col

    @api.multi
    def print_report_custom(self):
        tmp_name = '/tmp/invoice_report.xlsx'
        f_name = 'AS400' + '.xlsx'

        workbook = xlsxwriter.Workbook(tmp_name)
        worksheet = workbook.add_worksheet()
        move_line_ids = self.account_move_lines()

        row = 0
        col = 0

        url_format = workbook.add_format({'bold': 1})
        inv_line_color_url_format = workbook.add_format()
        inv_line_color_url_format.set_bg_color('green')

        credit_note_color_url_format = workbook.add_format()
        credit_note_color_url_format.set_bg_color('yellow')

        group_color_url_format = workbook.add_format()
        group_color_url_format.set_bg_color('blue')

        # Header Part ###
        header_part = ['FBHNR', 'FKTA', 'FKTNR', 'FBU#J', 'FBU#M', 'FBU#T', 'FBLGN', 'FBNR', 'FAG#J',
        'FAG#M', 'FAG#T', 'FABZA', 'FAGA', 'FAKSC', 'FAW', 'FBASC', 'FBASZ', 'FBF01', 'FBF02', 'FBF03',
        'FBF04', 'FBF05', 'FBF06', 'FBF07', 'FBF08', 'FBF09', 'FBF10', 'FBF11', 'FBF12', 'FBF13', 'FBF14',
        'FBF15', 'FBF16', 'FBF17', 'FBF18', 'FBF19', 'FBF20', 'FBF21', 'FBF22', 'FBF23', 'FBF24',
        'FBF25', 'FBF26', 'FBF27', 'FBF28', 'FBF29', 'FBF51', 'FBF52', 'FBF53', 'FBF54', 'FBF55',
        'FBF56', 'FBF57', 'FBF58', 'FBF59', 'FBF61', 'FBF62', 'FBF63', 'FBKVN', 'FBL#J', 'FBL#M',
        'FBL#T', 'FBLCK', 'FBLGA', 'FBPER', 'FBUSC', 'FBUTX', 'FBUVD', 'FDBLG', 'FFACN', 'FFL#J',
        'FFL#M', 'FFL#T', 'FGGKT', 'FGKTA', 'FHABN', 'FHBFW', 'FIVNR', 'FIVFN', 'FJONR', 'FKST',
        'FKTRG', 'FMA#J', 'FMA#M', 'FMA#T', 'FMAA', 'FMASP', 'FMAST', 'FMREF', 'FOPBT', 'FOPFW',
        'FOPS', 'FOPTX', 'FORDB', 'FPSKN', 'FRBNR', 'FRGA', 'FRGLN', 'FRGSP', 'FRZNR', 'FSART',
        'FSBNR', 'FSBS', 'FSH', 'FSK#J', 'FSK#M', 'FSK#T', 'FSKB', 'FSKBF', 'FSLFW', 'FSOLL', 'FSTNR',
        'FS2#J', 'FS2#M', 'FS2#T', 'FS2B', 'FS2BF', 'FUEK1', 'FUEK2', 'FUEK3', 'FUSI', 'FUSRL', 'FUSR2',
        'FUSR3', 'FUSSC', 'FUSS2', 'FUSS3', 'FVART', 'FVBMN', 'FVBNR', 'FVLT', 'FWC', 'FWJ#',
        'FZASP', 'FZLA', 'FZLSC', 'FZREF', 'FZSLK', 'FZSKZ', 'FBSRF', 'AED#', 'STS', 'TRKZ',
        'USR', 'ESD#']

        for val in header_part:
            worksheet.write(row, col, val, url_format)
            worksheet.set_column(row, col, 20)
            col += 1

        row += 1

        second_row = ['Buchhaltungsnummer', 'Kontoart', 'Kontonummer', 'Buchungsdatum: Jahr', 'Buchungsdatum: Monat',
        'Buchungsdatum: Tag', 'Belegnummer', 'Buchungsnummer', 'Ausgleichsdatum: Jahr',
        'Ausgleichsdatum: Monat', 'Ausgleichsdatum: Tag', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
        '', '', '', 'Bestellart VLS', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
        '', '', '', '', '', '', '', '', '', '', '', 'Belegdatum: Jahr', 'Belegdatum: Monat',
        'Belegdatum: Tag', '', 'Belegart', '', 'Buchungsschlüssel', 'Buchungstext', '',
        'Fremdbelegnummer', '', 'Fälligkeitsdatum: Jahr', 'Fälligkeitsdatum: Monat',
        'Fälligkeitsdatum: Tag', '', '', 'Habenbetrag', '', '', '', '',
        'Kostenstelle', 'Kostenträger', '', '', '', 'Mahnart', '', '', 'Mandatsreferenz', 'OP-Betrag', '',
        'OP-Status', '', '', '', 'Referenzbuchungsnummer', '', '', '', '', 'Satzart', '',
        'Sachbuchungssteuerung', 'Soll-Haben-Kennzeichen', 'Skontodatum: Jahr', 'Skontodatum: Monat',
        'Skontodatum: Tag', 'Skontobetrag', '', '', 'Sollbetrag', '', '', '', '',
        '', '', '', '', '', 'USt-ID', 'USt-Relation', 'USt-Relation: 2',
        'USt-Relation: 3', 'USt-Schlüssel', 'USt-Schlüssel: 2', 'USt-Schlüssel: 3', '', '', '', '', '',
        'Wirtschaftsjahr', '', 'Zahlungsart', 'Zahlungsschlüssel', '', '', '', '', '', 'Status', '', '', '']

        col = 0
        for val in second_row:
            worksheet.write(row, col, val)
            worksheet.set_column(row, col, 20)
            col += 1

        row += 1

        inv_move_line_ids = move_line_ids.filtered(lambda x: x.invoice_id and x.invoice_id.type == 'out_invoice')
        for move in inv_move_line_ids:
            col = 0
            if move.account_id.user_type_id.type == 'receivable':
                lst_vals = []

                company_id = move.company_id if move.company_id else ' '

                FBHNR = company_id.as400_company_code or ' '
                date_obj = datetime.datetime.strptime(move.date, '%Y-%m-%d')
                year, month, day = date_obj.strftime('%Y'), date_obj.strftime('%m'), date_obj.strftime('%d')

                lst_vals += [FBHNR, 'D', move.account_id.code, year, month, day, move.name]

                lst_vals += [' ' for i in range(1, 40)]
                lst_vals += ['0' for i in range(1, 13)]

                inv_date = move.invoice_id.date_invoice if move.invoice_id.date_invoice else move.date
                inv_date_obj = datetime.datetime.strptime(inv_date, '%Y-%m-%d')
                year, month, day = inv_date_obj.strftime('%Y'), inv_date_obj.strftime('%m'), inv_date_obj.strftime('%d')

                lst_vals += [' ', year, month, day, ' ', 'RE', ' ', "10", "Rechnung"]
                lst_vals += [' ' for i in range(1, 9)]
                lst_vals += [move.credit, "0", ]
                lst_vals += [' ' for i in range(1, 9)]

                as400_dunning_type = move.partner_id.as400_dunning_type if move.partner_id and move.partner_id.as400_dunning_type else ''
                lst_vals += [as400_dunning_type]

                lst_vals += [' ' for i in range(1, 3)]
                lst_vals += ["invoice_id.mandate_id.name"]
                lst_vals += ['0' for i in range(1, 3)]
                lst_vals += [' ' for i in range(1, 13)]

                fsh_val = 'H' if move.credit else 'S'
                lst_vals += [fsh_val]

                lst_vals += [' ' for i in range(1, 4)]
                lst_vals += ['0' for i in range(1, 4)]
                lst_vals += [move.debit]
                lst_vals += [' ' for i in range(1, 5)]
                lst_vals += ['0' for i in range(1, 3)]
                lst_vals += [' ' for i in range(1, 4)]

                FUSI_Val = move.partner_id.vat if (move.partner_id and move.partner_id.vat) else ''
                lst_vals += [
                            FUSI_Val, "Remaining FUSRL VAL", "Remaining FUSR2 VAL", "Remaining FUSR3 VAL", "Remaining FUSSC VAL",
                            "Remaining FUSS2 VAL", "Remaining FUSS3 VAL"]

                lst_vals += [' ' for i in range(1, 4)]

                # FVLT = 0 (zero / fix value)
                # FWJ# = date (only year)
                # FZLA = invoice_id.payment_mode_id -> AS400 Payment Mode (No.4)
                # FZLSC = invoice_id.payment_term_id -> AS400 Payment Term Code (No. 5)
                FZLA_val = move.invoice_id.payment_mode_id.id if move.invoice_id.payment_mode_id else ''
                FZLSC_val = move.invoice_id.payment_term_id.id if move.invoice_id.payment_term_id else ''
                lst_vals += ['0', " ", date_obj.strftime('%Y'), " ", FZLA_val, FZLSC_val]

                lst_vals += [' ' for i in range(1, 6)]
                lst_vals += ['A']
                lst_vals += [' ' for i in range(1, 4)]

                col = self._write_list_data(worksheet, row, col, lst_vals, inv_line_color_url_format)

                row += 1

        credit_note_move_line_ids = move_line_ids.filtered(lambda x: x.invoice_id and x.invoice_id.type == 'out_refund')
        for move in credit_note_move_line_ids:
            col = 0
            if move.account_id.user_type_id.type == 'receivable':
                lst_vals = []

                company_id = move.company_id if move.company_id else ' '

                FBHNR = company_id.as400_company_code or ' '
                date_obj = datetime.datetime.strptime(move.date, '%Y-%m-%d')
                year, month, day = date_obj.strftime('%Y'), date_obj.strftime('%m'), date_obj.strftime('%d')

                lst_vals += [FBHNR, 'D', move.account_id.code, year, month, day, move.name]

                lst_vals += [' ' for i in range(1, 40)]
                lst_vals += ['0' for i in range(1, 13)]

                inv_date = move.invoice_id.date_invoice if move.invoice_id.date_invoice else move.date
                inv_date_obj = datetime.datetime.strptime(inv_date, '%Y-%m-%d')
                year, month, day = inv_date_obj.strftime('%Y'), inv_date_obj.strftime('%m'), inv_date_obj.strftime('%d')

                lst_vals += [' ', year, month, day, ' ', 'GS', ' ', "15", "Gutschrift"]
                lst_vals += [' ' for i in range(1, 9)]
                lst_vals += [move.credit, "0", ]
                lst_vals += [' ' for i in range(1, 9)]

                as400_dunning_type = move.partner_id.as400_dunning_type if move.partner_id and move.partner_id.as400_dunning_type else ''
                lst_vals += [as400_dunning_type]

                lst_vals += [' ' for i in range(1, 3)]
                lst_vals += ["invoice_id.mandate_id.name"]
                lst_vals += ['0' for i in range(1, 3)]
                lst_vals += [' ' for i in range(1, 13)]

                fsh_val = 'H' if move.credit else 'S'
                lst_vals += [fsh_val]

                lst_vals += [' ' for i in range(1, 4)]
                lst_vals += ['0' for i in range(1, 4)]
                lst_vals += [move.debit]
                lst_vals += [' ' for i in range(1, 5)]
                lst_vals += ['0' for i in range(1, 3)]
                lst_vals += [' ' for i in range(1, 4)]

                FUSI_Val = move.partner_id.vat if (move.partner_id and move.partner_id.vat) else ''
                lst_vals += [
                            FUSI_Val, "Remaining FUSRL VAL", "Remaining FUSR2 VAL", "Remaining FUSR3 VAL", "Remaining FUSSC VAL",
                            "Remaining FUSS2 VAL", "Remaining FUSS3 VAL"]

                lst_vals += [' ' for i in range(1, 4)]

                # FVLT = 0 (zero / fix value)
                # FWJ# = date (only year)
                # FZLA = invoice_id.payment_mode_id -> AS400 Payment Mode (No.4)
                # FZLSC = invoice_id.payment_term_id -> AS400 Payment Term Code (No. 5)
                FZLA_val = move.invoice_id.payment_mode_id.id if move.invoice_id.payment_mode_id else ''
                FZLSC_val = move.invoice_id.payment_term_id.id if move.invoice_id.payment_term_id else ''
                lst_vals += ['0', " ", date_obj.strftime('%Y'), " ", FZLA_val, FZLSC_val]

                lst_vals += [' ' for i in range(1, 6)]
                lst_vals += ['A']
                lst_vals += [' ' for i in range(1, 4)]

                col = self._write_list_data(worksheet, row, col, lst_vals, credit_note_color_url_format)

                row += 1

        account_ids = move_line_ids.mapped('account_id').filtered(lambda x: x.user_type_id.type != 'receivable')
        for acc in account_ids:
            group_move_line_ids = move_line_ids.filtered(lambda x: x.account_id == acc)
            for move in group_move_line_ids:
                col = 0

                company_id = move.company_id if move.company_id else ' '

                lst_vals = []

                FBHNR = company_id.as400_company_code or ' '

                date_obj = datetime.datetime.strptime(move.date, '%Y-%m-%d')
                year, month, day = date_obj.strftime('%Y'), date_obj.strftime('%m'), date_obj.strftime('%d')

                lst_vals += [FBHNR, 'S', move.account_id.code, year, month, day, move.account_id.id]

                lst_vals += [' ' for i in range(1, 40)]
                lst_vals += ['0' for i in range(1, 13)]

                inv_date = move.invoice_id.date_invoice if move.invoice_id.date_invoice else move.date
                inv_date_obj = datetime.datetime.strptime(inv_date, '%Y-%m-%d')
                year, month, day = inv_date_obj.strftime('%Y'), inv_date_obj.strftime('%m'), inv_date_obj.strftime('%d')
                FBLGA_val = 'H' if move.credit else "S"

                lst_vals += [' ', year, month, day, ' ', FBLGA_val, ' ', "40", ""]
                lst_vals += [' ' for i in range(1, 9)]
                lst_vals += [move.credit, "0", ]
                lst_vals += [' ' for i in range(1, 4)]

                FKST_val = '18000' if acc.user_type_id.name == 'Income' else ''
                FKTRG_val = '99999999' if acc.user_type_id.name == 'Income' else ''

                lst_vals += [FKST_val, FKTRG_val]
                lst_vals += [' ' for i in range(1, 4)]

                as400_dunning_type = move.partner_id.as400_dunning_type if move.partner_id and move.partner_id.as400_dunning_type else ''
                lst_vals += [as400_dunning_type]

                lst_vals += [' ' for i in range(1, 3)]
                lst_vals += ["invoice_id.mandate_id.name"]
                lst_vals += ['0' for i in range(1, 3)]
                lst_vals += [' ' for i in range(1, 13)]

                fsh_val = 'H' if move.credit else 'S'
                lst_vals += [fsh_val]

                lst_vals += [' ' for i in range(1, 4)]
                lst_vals += ['0' for i in range(1, 4)]
                lst_vals += [move.debit]
                lst_vals += [' ' for i in range(1, 5)]
                lst_vals += ['0' for i in range(1, 3)]
                lst_vals += [' ' for i in range(1, 4)]

                FUSI_Val = move.partner_id.vat if (move.partner_id and move.partner_id.vat) else ''
                lst_vals += [FUSI_Val]
                lst_vals += ['0' for i in range(1, 4)]
                lst_vals += [' ' for i in range(1, 7)]

                # FVLT = 0 (zero / fix value)
                # FWJ# = date (only year)
                # FZLA = invoice_id.payment_mode_id -> AS400 Payment Mode (No.4)
                # FZLSC = invoice_id.payment_term_id -> AS400 Payment Term Code (No. 5)
                FZLA_val = move.invoice_id.payment_mode_id.id if move.invoice_id.payment_mode_id else ''
                FZLSC_val = move.invoice_id.payment_term_id.id if move.invoice_id.payment_term_id else ''
                lst_vals += ['0', " ", date_obj.strftime('%Y')]

                lst_vals += [' ' for i in range(1, 9)]
                lst_vals += ['A']
                lst_vals += [' ' for i in range(1, 4)]

                col = self._write_list_data(worksheet, row, col, lst_vals, group_color_url_format)

                row += 1

        worksheet.freeze_panes(10, 4)  # Freeze first row 10 and first 4 columns.
        workbook.close()

        with open(tmp_name, 'rb') as fp:
            data = fp.read()
            fp.close()

        out = base64.encodestring(data)

        # Files actions
        attach_vals = {'invoice_data': f_name, 'file_name': out, 'start_date': self.start_date, 'end_date': self.end_date}
        act_id = self.env['account.move.report.as.400'].create(attach_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.report.as.400',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
