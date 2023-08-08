from odoo import models, fields, api, _


class SmartProvisionAccounting(models.Model):
    _name = 'smart.provision.accounting'

    provision_account = fields.Many2one('account.account')
    name = fields.Char('Provision')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    _sql_constraints = [
        ('name_unique', 'unique(name)', ' Provision already exists!')
    ]

