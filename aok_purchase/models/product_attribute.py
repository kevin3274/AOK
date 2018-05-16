# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AttributeChecklistCategory(models.Model):
    _name = "attributes.checklist.category"

    name = fields.Char(string='Name', translate=True)
    attribute_ids = fields.One2many('attributes.checklist', 'category_id', string='Attributes')
    description = fields.Html(string='Description')


class AttributeChecklist(models.Model):
    _name = "attributes.checklist"

    name = fields.Char(string='Attribute Name', translate=True)
    category_id = fields.Many2one('attributes.checklist.category', string='Category')


class ProductAttributesChecklist(models.Model):
    _name = "product.attributes.checklist"

    name = fields.Many2one("attributes.checklist", string="Attribute Name")
    product_id = fields.Many2one('product.product', string='Product')
    value = fields.Char('Value')


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains('checklist_ids', 'checklist_ids.name', 'checklist_ids.value')
    def _check_mandatory(self):
        for record in self:
            for attribute in record.checklist_ids:
                if attribute.name and attribute.name.name and attribute.name.name[-1] == '*':
                    if not attribute.value:
                        raise ValidationError(_("Please fill the mandatory Checklist Attribute Value."))
