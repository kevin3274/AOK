# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    organisation_id = fields.Many2one('res.partner', string='Organisation')
