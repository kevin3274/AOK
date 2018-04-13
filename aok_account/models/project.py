# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    product_analytic_id = fields.Many2one("product.product", string="Analytic Product")

    _sql_constraints = [
        ('product_uniq', 'unique(product_analytic_id)', 'Product can be used in only one Project.'),
    ]

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        self.env['account.analytic.default'].create({'product_id': res.product_analytic_id.id, 'analytic_id': res.analytic_account_id.id})
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    project_count = fields.Integer(compute="_compute_project_count", string="Projects")

    def _compute_project_count(self):
        Project = self.env['project.project']
        for product in self:
            product.project_count = Project.search_count([('product_analytic_id', '=', product.id)])

    @api.multi
    def view_projects(self):
        projects = self.env['project.project'].search([('product_analytic_id', '=', self.id)])
        action = self.env.ref('project.open_view_project_all').read()[0]
        action['domain'] = [('id', 'in', projects.ids)]
        return action


class ProductTemplate(models.Model):
    _inherit = "product.template"

    project_count = fields.Integer(compute="_compute_project_count", string="Projects")

    def _compute_project_count(self):
        Project = self.env['project.project']
        Product = self.env['product.product']
        for template in self:
            products = Product.search([('product_tmpl_id', '=', template.id)])
            template.project_count = Project.search_count([('product_analytic_id', 'in', products.ids)])

    @api.multi
    def view_projects(self):
        self.ensure_one()
        products = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        projects = self.env['project.project'].search([('product_analytic_id', 'in', products.ids)])
        action = self.env.ref('project.open_view_project_all').read()[0]
        action['domain'] = [('id', 'in', projects.ids)]
        return action
