from odoo import models, api, fields, exceptions


class SendNewProduct(models.TransientModel):
    _name = 'send.new.product.wizard'

    date = fields.Date(
        string='Subs to'
    )

    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product'
    )

    @api.multi
    def send_product(self):
        self.ensure_one()

        SaleOrderModel = self.env['sale.order']
        SaleOrderLineModel = self.env['sale.order.line']

        product_id = self._context.get('active_id', False)

        if not product_id:
            raise exceptions.MissingError('Product_id does not exist.')

        orders = SaleOrderModel.search([
            ('subs_to', '>=', self.date),
            ('order_line.product_id.product_tmpl_id', '=', product_id)
        ])

        for order in orders:
            lines = order.order_line.filtered(lambda x: x.product_id.id == product_id)

            qty = 0
            for line in lines:
                qty += line.product_uom_qty

            new_line = SaleOrderLineModel.create({
                'product_id' : self.product_id.id,
                'product_uom_qty': qty,
                'order_id': order.id
            })
            new_line.product_id_change()
            new_line.product_uom_change()

        return True