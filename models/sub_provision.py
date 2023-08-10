from odoo import models, fields, api, _


class SmartProvisionAccounting(models.Model):
    _name = 'smart.provision.accounting'
    _description = 'Smart Provision Accounting'

    provision_account = fields.Many2one('account.account')
    name = fields.Char('Provision')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', ' Provision already exists!')
    ]

