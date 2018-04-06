# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    kommissionierhinweis = fields.Char(string='Kommissionierhinweis')

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        order = self.env['sale.order'].search([('name', '=', res.origin)])
        if order:
            res.kommissionierhinweis = order.kommissionierhinweis
        return res


class StockPickingRoute(models.Model):
    _name = "stock.picking.route"
    _order = 'sequence'

    location_id = fields.Many2one('stock.location', string='Location')
    sequence = fields.Integer(required=True, default=10)

