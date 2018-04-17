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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    send_list = fields.Boolean(
        string='Send list'
    )

    no_magazines = fields.Integer(
        string='No magazines'
    )

    crm_lead = fields.Char(
        string='CRM-ID'
    )

    enc_name = fields.Char(
        string='Name'
    )

    enc_lastname = fields.Char(
        string='Lastname'
    )

    enc_date = fields.Date(
        string='Date of Birth'
    )

    enc_insurance_number = fields.Integer(
        string='Insurance Number'
    )

    enc_insurance_status = fields.Integer(
        string='Insurance Status'
    )

    _sql_constraints = [
        ('email_uniq', 'unique (email)', "Email address already exists!"),
    ]


