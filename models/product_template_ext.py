from odoo import _, api, fields, models

class ProductTemplateExt(models.Model):
    _inherit = 'product.template'

    # is_inherit_provisions = fields.Boolean(string='Inherit Provisions ?', default=True)