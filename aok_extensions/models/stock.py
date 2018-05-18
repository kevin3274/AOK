##############################################################################
#
# Copyright (c) 2018 - Now Modoolar (http://modoolar.com) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract support@modoolar.com
#
##############################################################################

from odoo import models, fields, api


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    actual_stock = fields.Integer(
        string='Actual Stock',
        compute='_calculate_actual_stock'
    )

    check_point = fields.Float(
        compute="_calculate_check_point"
    )

    @api.multi
    def _calculate_actual_stock(self):
        # TODO: We should definitely optimize this.
        StockLocationModel = self.env['stock.location']
        query = "SELECT sum(quantity) FROM stock_quant " \
                "WHERE location_id IN %s AND product_id = %s"

        for record in self:
            locations = StockLocationModel.search([
                ('id', 'child_of', record.location_id.id)
            ])
            self.env.cr.execute(
                query,
                [tuple(locations.ids), record.product_id.id]
            )
            record.actual_stock = self.env.cr.fetchall()[0][0]

    @api.multi
    def _calculate_check_point(self):
        for record in self:
            record.check_point = record.actual_stock - record.product_min_qty
