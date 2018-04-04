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

    remaining_qty = fields.Float(string='Remaining Qty', compute='_compute_remaining_qty')
    state = fields.Selection(related='requisition_id.state', string='Status')
    vendor_id = fields.Many2one(related='requisition_id.vendor_id', string='Vendor')
    order_count = fields.Integer(related='requisition_id.order_count', string='Number of Orders')
    description = fields.Text(related='requisition_id.description', string='Description')
    warehouse_id = fields.Many2one(related='requisition_id.warehouse_id', string='Warehouse')
    origin = fields.Char(related='requisition_id.origin', string='Source Document')
    type_id = fields.Many2one(related='requisition_id.type_id', string='Agreement Type')
    name = fields.Char(related='requisition_id.name', string='Agreement Reference')


class PurchaseRequisitionType(models.Model):
    _inherit = "purchase.requisition.type"

    show_remaining_quantity = fields.Boolean(string='Show remaining quantity on product form', default=False)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def compute_remaining_qty(self):
        purchase_requisition_lines = self.mapped('purchase_requisition_line_ids')
        for line in purchase_requisition_lines:
            if line.requisition_id and line.requisition_id.state == 'open' and line.requisition_id.type_id.show_remaining_quantity:
                self.requisition_remaining_qty += line.remaining_qty

    purchase_requisition_line_ids = fields.One2many('purchase.requisition.line', 'product_id', string='Purchase Requisition Line')
    requisition_remaining_qty = fields.Integer(string='Remaining Quantity', compute='compute_remaining_qty')

    @api.multi
    def action_view_purchase_requisition_line(self):
        action = self.env.ref('aok_purchase.action_purchase_requisition_line').read()[0]

        purchase_requisition_lines = self.mapped('purchase_requisition_line_ids').filtered(lambda x: x.type_id.show_remaining_quantity)
        if len(purchase_requisition_lines) > 1:
            action['domain'] = [('id', 'in', purchase_requisition_lines.ids)]
        elif purchase_requisition_lines:
            action['domain'] = [('id', 'in', purchase_requisition_lines.ids), ('state', '=', 'open')]
            action['res_id'] = purchase_requisition_lines.id
        return action
