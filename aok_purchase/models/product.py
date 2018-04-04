# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductSupplierinfoFixedCosts(models.Model):
    _name = 'product.supplierinfo.fixed.costs'

    cost_category = fields.Char(string='Kostenkategorie', translate=True)
    amount = fields.Float(string='Betrag')


class ProductSupplierinfoVariableCosts(models.Model):
    _name = 'product.supplierinfo.variable.costs'

    cost_category = fields.Char(string='Kostenkategorie', translate=True)
    amount = fields.Float(string='Betrag')


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    def _total_uom_amount(self):
    	self.total_price = self.price + sum(self.fix_cost_ids.amount) / self.min_qty + sum(self.variable_cost_ids.amount)


    fix_cost_ids = fields.Many2many('product.supplierinfo.fixed.costs', string='Product Returns')
    variable_cost_ids = fields.Many2many('product.supplierinfo.variable.costs', string='Initial Cost')
    total_price = fields.Monetary(string="Gesamtpreis/ME", compute='_total_uom_amount')
    sim_sales_price = fields.Float(string='Sim Sales Proce')
    margin_per = fields.Float(string='Margin (%)')
    margin_eur = fields.Float(string='Margin (€)')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    seller_ids = fields.One2many(copy=True)


class ProductProduct(models.Model):
    _inherit = "product.product"

    checklist_category_id = fields.Many2one('attributes.checklist.category', string='Checklist Category')
    checklist_ids = fields.Many2many('attributes.checklist', string='Checklist Attribute')
    description = fields.Html(string='Additional Information')
    sustained = fields.Boolean(string='Nachhaltig')
    delivery_strategy = fields.Selection([
        ('direktauslieferung', 'Direktauslieferung'),
        ('verteiler', 'Verteiler'),
        ('teil-direktauslieferung', 'Teil-Direktauslieferung'),
        ('einlagerung', 'Einlagerung')], string='Delivery Strategy')

    def action_load_attribute_category(self):
        if self.checklist_category_id:
            for attribute in self.checklist_category_id.attribute_ids:
                self.checklist_ids = [(4, attribute.id, None) for attribute in self.checklist_category_id.attribute_ids]

    @api.onchange('checklist_category_id')
    def _onchange_checklist_category_id(self):
        self.checklist_ids = False
