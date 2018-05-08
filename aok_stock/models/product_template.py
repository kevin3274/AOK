# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    dangerous_goods_number = fields.Char(string='Dangerous goods number')


class ProductProduct(models.Model):
    _inherit = "product.product"

    kit_qty = fields.Float(string='Kit Quantity')

    def _get_kit_qty(self):
        MrpBom = self.env['mrp.bom']
        bom = MrpBom._bom_find(product_tmpl=self.product_tmpl_id, product=self, company_id=self.company_id.id)
        if bom and bom.type == "phantom":
            products = {}
            for line in bom.bom_line_ids:
                # Calculate product quantity based on uom
                qty = line.product_qty
                product_uom_type = line.product_uom_id.uom_type
                product_uom_factor = line.product_uom_id.factor_inv
                if product_uom_type == 'bigger':
                    qty = line.product_qty * product_uom_factor
                elif product_uom_type == 'smaller':
                    qty = line.product_qty / product_uom_factor
                if line.product_id.id in products.keys():
                    products[line.product_id.id]['qty'] += qty
                else:
                    products.update({line.product_id.id: {'qty_available': line.product_id.virtual_available, 'qty': qty}})
            possible_qty = []
            for p in products:
                possible_qty.append(int(products[p]['qty_available'] / products[p]['qty']))
            if possible_qty:
                return min(possible_qty)
        return 0.0

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_quantities(self):
        super(ProductProduct, self)._compute_quantities()
        for product in self:
            product.kit_qty = product._get_kit_qty()
