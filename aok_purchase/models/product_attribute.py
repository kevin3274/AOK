# -*- coding: utf-8 -*-

from odoo import fields, models


class AttributeChecklist(models.Model):
    _name = "attributes.checklist"

    name = fields.Char(string='Attribute Name', translate=True)
    category_id = fields.Many2one('attributes.checklist.category', string='Category')
    product_id = fields.Many2one('product.product', string='Product')
    value = fields.Char('Value')

class AttributeChecklistCategory(models.Model):
    _name = "attributes.checklist.category"

    name = fields.Char(string='Name', translate=True)
    attribute_ids = fields.One2many('attributes.checklist', 'category_id', string='Attributes')


class ProductAttributesChecklist(models.Model):
    _name = "product.attributes.checklist"

    product_id = fields.Many2one('product.product', string='Product')
    checklist_id = fields.Many2one('attributes.checklist', string='Attribute Checklist')
    checklist_category = fields.Many2one(related='checklist_id.category_id', string='Checklist Category')
    
