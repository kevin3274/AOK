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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    published = fields.Selection(
        selection=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly')
        ],
        string='Published'
    )

    isbn_number = fields.Char(
        string='ISBN Number',
    )

    page_number = fields.Integer(
        string='Page Number'
    )

    printing = fields.Integer(
        string='Printing'
    )

    no_subscription = fields.Integer(
        string='No subscription'
    )

    copyright = fields.Char(
        string='Copyright'
    )

    product_performance = fields.Text(
        string='Product Performance'
    )

    # General Information

    prev_product_id = fields.Many2one(
        comodel_name='product.template',
        string='Previous product'
    )

    tag_ids = fields.Many2many(
        comodel_name='product.template.tag',
        relation='tag_product_rel',
        column1='product_id',
        column2='tag_id',
        string='Tags'
    )

    # Purchase Information

    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible'
    )

    competency_tag_ids = fields.Many2many(
        comodel_name='product.template.competency.tag',
        relation='competency_tag_product_rel',
        column1='product_id',
        column2='competency_tag_id',
        string='Competency Tags'
    )

    # Internal Reference

    @api.model
    def create(self, vals):
        """ If we didn't set Internal reference create it automatically
        This works only if we crate product from product.template form
        """
        if not self._context.get('create_product_product', False):
            if ('default_code' not in vals or not vals['default_code']):
                IrSequenceModel = self.env['ir.sequence']
                vals['default_code'] = IrSequenceModel.next_by_code('product.internal.reference')
        return super(ProductTemplate, self).create(vals)


    _sql_constraints = [
        ('default_code_uniq', 'unique (default_code)', "Internal reference already exists!"),
    ]

    # Quotations

    quotations_count = fields.Integer(
        compute='_compute_quotations_count',
        string='Quotations'
    )

    @api.multi
    def _compute_quotations_count(self):
        """ Calculate number of Quotations with specific product """
        SaleOrderModel = self.env['sale.order']

        for record in self:
            cnt = SaleOrderModel.search_count([
                ('order_line.product_id.product_tmpl_id.id', '=', record.id),
                ('state', 'in', ['draft', 'sent']),
            ])
            record.quotations_count = cnt

    @api.multi
    def action_view_quotations(self):
        """ Open Quotation List view with quotations which have specific product """
        self.ensure_one()

        SaleOrderLineModel = self.env['sale.order.line']
        IrActionModel = self.env['ir.actions.act_window']

        lines = SaleOrderLineModel.search([
            ('product_id.product_tmpl_id.id', '=', self.id)
        ])

        action = IrActionModel.for_xml_id('sale', 'action_quotations')
        action.update({
            'domain': [
                ('state', 'in', ['draft', 'sent']),
                ('id', 'in', lines.mapped('order_id').ids)
            ]
        })

        return action

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        """ If we didn't set Internal reference create it automatically
        This works only if we crate product from product.product form
        """
        if not self._context.get('create_from_tmpl', False):
            IrSequenceModel = self.env['ir.sequence']
            vals['default_code'] = IrSequenceModel.next_by_code('product.internal.reference')
        return super(ProductProduct, self).create(vals)


class ProductAbstractTag(models.AbstractModel):
    _name = 'product.abstract.tag'
    _description = 'Product Abstract Tag'

    name = fields.Char(
        string='Tag Name',
        required=True,
        index=True,
        translate=True
    )

    color = fields.Integer(
        string='Color Index'
    )

    active = fields.Boolean(
        default=True,
        help="The active field allows you to hide the category without removing it."
    )


class ProductTemplateTag(models.Model):
    _name = 'product.template.tag'
    _inherit = 'product.abstract.tag'
    _description = 'Product Tags'

    product_ids = fields.Many2many(
        comodel_name='product.template',
        relation='tag_product_rel',
        column1='tag_id',
        column2='product_id',
        string='Products'
    )


class ProductTemplateCompetencyTag(models.Model):
    _name = 'product.template.competency.tag'
    _inherit = 'product.abstract.tag'
    _description = 'Product Competency Tags'

    product_ids = fields.Many2many(
        comodel_name='product.template',
        relation='competency_tag_product_rel',
        column1='competency_tag_id',
        column2='product_id',
        string='Products'
    )
