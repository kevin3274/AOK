# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_note = fields.Char(string='Kommissionierhinweis')

    qc_overpacked = fields.Boolean("Palette überpackt")
    qc_unpaletted = fields.Boolean("Unpalettiert geladen")
    qc_false_uom = fields.Boolean("Verp-Einheit falsch")
    qc_mixed_quality = fields.Boolean("Nicht sortenrein")
    qc_no_do = fields.Boolean("Lieferschein fehlt")
    qc_higher_140 = fields.Boolean("Höher als 140 cm")
    qc_oversized = fields.Boolean("Zu Lang / Zu breit")
    qc_unlabeled = fields.Boolean("Karton Unbeschriftet")
    qc_false_label = fields.Boolean("Beschr. Lief.-Hinw.")
    qc_no_reference = fields.Boolean("Best-/Art.-Nr. fehlt")

    qc_note = fields.Text("Fehler/sonstiges")
    qc_time = fields.Float("Zeitbedarf")

    qc_processing = fields.Char("Verarbeitung")
    qc_print = fields.Char("Druck")
    qc_packaging = fields.Char("Verpackung")
    qc_functional_test = fields.Char("Funktionstest")

    picking_nok = fields.Boolean()

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        order = self.env['sale.order'].search([('name', '=', res.origin)])
        if order:
            res.picking_note = order.picking_note
        return res


class StockPickingRoute(models.Model):
    _name = "stock.picking.route"
    _order = 'sequence'

    location_id = fields.Many2one('stock.location', string='Location')
    sequence = fields.Integer(required=True, default=10)

