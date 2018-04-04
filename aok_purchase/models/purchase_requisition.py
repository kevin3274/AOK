# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    competency_id = fields.Many2one('core.competency', string='Competency')
    salesman_id = fields.Many2one('res.users', string='Salesman')


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.product_qty - line.qty_ordered

    name = fields.Char(related='requisition_id.name', string='Agreement Reference')
    remaining_qty = fields.Float(string='Remaining Qty', compute='_compute_remaining_qty')
    state = fields.Selection(related='requisition_id.state', string='Status')
    vendor_id = fields.Many2one("res.partner", related='requisition_id.vendor_id', string='Vendor', store=True)
    order_count = fields.Integer(related='requisition_id.order_count', string='Number of Orders')
    description = fields.Text(related='requisition_id.description', string='Description')
    warehouse_id = fields.Many2one(related='requisition_id.warehouse_id', string='Warehouse')
    origin = fields.Char(related='requisition_id.origin', string='Source Document')
    type_id = fields.Many2one(related='requisition_id.type_id', string='Agreement Type')
    ordering_date = fields.Date(related='requisition_id.ordering_date', string='Ordering Date', store=True)


class PurchaseRequisitionType(models.Model):
    _inherit = "purchase.requisition.type"

    show_remaining_quantity = fields.Boolean(string='Show remaining quantity on product form', default=False)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_remaining_qty(self):
        RequisitionLine = self.env['purchase.requisition.line']
        for product in self:
            purchase_requisition_lines = RequisitionLine.search([('product_id', '=', product.id), ('state', '=', 'open')])
            purchase_requisition_lines = purchase_requisition_lines.filtered(lambda x: x.type_id.show_remaining_quantity)
            product.requisition_remaining_qty = sum(purchase_requisition_lines.mapped('remaining_qty'))

    requisition_remaining_qty = fields.Integer(string='Remaining Quantity', compute='_compute_remaining_qty')

    @api.multi
    def action_view_purchase_requisition_line(self):
        self.ensure_one()
        action = self.env.ref('aok_purchase.action_purchase_requisition_line').read()[0]
        purchase_requisition_lines = self.env['purchase.requisition.line'].search([('product_id', '=', self.id), ('state', '=', 'open')])
        purchase_requisition_lines = purchase_requisition_lines.filtered(lambda x: x.type_id.show_remaining_quantity)
        action['domain'] = [('id', 'in', purchase_requisition_lines.ids)]
        return action
