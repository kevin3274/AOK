# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    organisation_id = fields.Many2one('res.partner', string='Organisation')

    @api.depends('is_company', 'parent_id.commercial_partner_id', 'organisation_id')
    def _compute_commercial_partner(self):
        for partner in self:
            if partner.is_company or not partner.parent_id:
                partner.commercial_partner_id = partner.organisation_id or partner
            else:
                partner.commercial_partner_id = partner.organisation_id or partner.parent_id.commercial_partner_id
