# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    dangerous_goods_number = fields.Char(string='Dangerous goods number')
