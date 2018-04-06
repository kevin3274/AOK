# -*- coding: utf-8 -*-

from odoo import fields, models

class StockMove(models.Model):
    _inherit = "stock.move"

    partner_id = fields.Many2one(related='picking_id.partner_id', string='Partner')
