from odoo import models, fields, api, _


class SmartProvision(models.Model):
    _name = 'smart.provision'
    _description = 'Provision'
    _rec_name = 'provision_id'

    # Float Fields
    percentage_value = fields.Float(string='Percentage')
    subtotal = fields.Float(string='Subtotal')
    active = fields.Boolean(default=True)

    # Relational Fields
    product_category_id = fields.Many2one('product.category', string='Product Category')
    provision_id = fields.Many2one('smart.provision.accounting', string='Provision Name', ondelete='restrict')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    # Can Not Create Category and Provision With Same Values
    _sql_constraints = [
        ('record_unique', 'unique(product_category_id, provision_id,percentage_value)',
         ' Provision already exists in same category!')
    ]

    @api.onchange('company_id')
    def company_domain(self):
        return {'domain': {'provision_id': [('company_id', '=', self.env.company.id)]}}


class ProductCategory(models.Model):
    _inherit = 'product.category'

    provision_count = fields.Integer(compute='compute_count')

    # Computing The Provisions In  Our Product Categoy
    def compute_count(self):
        for record in self:
            record.provision_count = self.env['smart.provision'].search_count(
                [('product_category_id', '=', self.id)])

    # Opens Tree View of All Provisions in Current Category
    def get_provisions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Provisions',
            'view_mode': 'tree,form',
            'res_model': 'smart.provision',
            'domain': [('product_category_id', '=', self.id)],
            'context': {'create': True, 'default_product_category_id': self.id}
        }


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    provision_ids = fields.Many2many('smart.provision', string='Provisions', ondelete='restrict')
    provisioned = fields.Boolean(default=False)
    quantity_set = fields.Boolean(default=False)

    # is_provisions_readonly =fields.Boolean(default=True)

    # When we Select a Product in Purchase Order This Function Will Add the Provision According to Product Category
    @api.onchange('product_id')
    def check_provision_names(self):
        product = self.env['product.template'].search([('id', '=', self.product_id.product_tmpl_id.id)])
        for rec in self:
            base_categ_id = rec.product_id.categ_id
            all_provisions = []
            status = True
            while status == True:
                if base_categ_id:
                    categ_provisions = rec.env['smart.provision'].search(
                        [('product_category_id', '=', base_categ_id.id)]).ids
                    if categ_provisions:
                        for provision in categ_provisions:
                            all_provisions.append(provision)
                        status = False
                        rec.provision_ids = all_provisions
                    else:
                        base_categ_id = base_categ_id.parent_id
                else:
                    status = False

        # One Parent Provision

        # if product.is_inherit_provisions == True:
        #     for rec in self:
        #         rec.is_provisions_readonly = True
        #         base_categ_id = rec.product_id.categ_id
        #         all_provisions = []
        #         status = True
        #         if rec.product_id.categ_id:
        #             if status == True:
        #                 while status == True:
        #                     if rec.product_id.categ_id:
        #                         categ_provisions = rec.env['smart.provision'].search([('product_category_id', '=', rec.product_id.categ_id.id)]).ids
        #                         if categ_provisions:
        #                             for provision in categ_provisions:
        #                                 all_provisions.append(provision)
        #                         if rec.product_id.categ_id.parent_id:
        #                             parent = rec.product_id.categ_id.parent_id
        #                             categ_provisions = rec.env['smart.provision'].search([('product_category_id', '=', parent.id)]).ids
        #                             if categ_provisions:
        #                                 for category in categ_provisions:
        #                                     all_provisions.append(category)
        #                                 rec.provision_ids = all_provisions
        #                                 rec.product_id.categ_id = base_categ_id
        #                                 status = False
        #                             else:
        #                                 rec.product_id.categ_id = rec.product_id.categ_id.parent_id
        #             else:
        #                 rec.provision_ids = all_provisions
        #                 rec.product_id.categ_id = base_categ_id
        #                 status = False
        # else:
        #     for rec in self:
        #         rec.is_provisions_readonly = False

        # For all Parents Provisions
        # if rec.product_id.categ_id:
        #     while status == True:
        #         if rec.product_id.categ_id:
        #             categ_provisions = rec.env['smart.provision'].search([('product_category_id', '=', rec.product_id.categ_id.id)]).ids
        #             if categ_provisions:
        #                 for provision in categ_provisions:
        #                     all_provisions.append(provision)
        #             if rec.product_id.categ_id.parent_id:
        #                 rec.product_id.categ_id = rec.product_id.categ_id.parent_id
        #             else:
        #                 rec.provision_ids = all_provisions
        #                 rec.product_id.categ_id = base_categ_id
        #                 status = False

    # This Pop-up Will Show All The Provisions Our Product Have and Calculate the Price
    def provision_popup(self):
        self.ensure_one()
        provisions = self.provision_ids
        for line in provisions:
            subtotal = (line.percentage_value * self.price_unit)
            line.write({
                'subtotal': subtotal,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Provisions',
            'view_mode': 'tree',
            'target': 'new',
            'res_model': 'smart.provision',
            'views': [(self.env.ref('provision.smart_provision_view_tree2').id, 'tree')],
            'domain': [('id', 'in', self.provision_ids.ids)],
            'context': {'create': False},
        }
