# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_note = fields.Char(string='Kommissionierhinweis')
