# -*- coding: utf-8 -*-

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    dangerous_goods_number = fields.Char(related="product_id.product_tmpl_id.dangerous_goods_number", string='Dangerous goods number', store=True)
    partner_id = fields.Many2one(related='picking_id.partner_id', string='Partner', store=True)
