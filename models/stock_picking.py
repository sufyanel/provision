from odoo import _, api, fields, models
from contextlib import contextmanager
from odoo.tools import format_amount
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for rec in self:
            if rec.picking_type_code == 'incoming':
                for new_line in rec.move_ids:
                    if new_line.purchase_line_id and new_line.purchase_line_id.provision_ids and not new_line.purchase_line_id.provisioned:
                        new_line.purchase_line_id.update({
                            'price_unit': sum(new_line.purchase_line_id.provision_ids.mapped(
                                'percentage_value')) * new_line.purchase_line_id.price_unit + new_line.purchase_line_id.price_unit if new_line.purchase_line_id else new_line.purchase_line_id.price_unit,
                            'provisioned': True,
                            'quantity_set': False,
                        })
        result = super(StockPicking, self).button_validate()
        for rec in self:
            if rec.picking_type_code == 'incoming':
                debit_dict = {}
                for new_line in rec.move_ids:
                    if new_line.purchase_line_id and new_line.purchase_line_id.provision_ids:
                        product_price = (new_line.purchase_line_id.price_unit / ((
                                                                                         sum(new_line.purchase_line_id.provision_ids.mapped(
                                                                                             'percentage_value')) * 100) + 100)) * 100
                        for l in new_line.account_move_ids.invoice_line_ids:
                            if l.debit > 0:
                                l.update({
                                    'debit': product_price * new_line.quantity_done
                                })
                                debit_dict['account_id'] = l.account_id.id
                                debit_dict['partner_id'] = l.partner_id.id
                                debit_dict['name'] = l.name
                                debit_dict['move_id'] = l.move_id.id
                            if l.credit > 0:
                                l.update({
                                    'credit': product_price * new_line.quantity_done
                                })
                        provisions = new_line.purchase_line_id.provision_ids
                        for provision in provisions:
                            new_line.account_move_ids.write({'invoice_line_ids': [
                                (0, 0, {'account_id': provision.provision_id.provision_account.id,
                                        'partner_id': new_line.account_move_ids.partner_id.id,
                                        'name': provision.provision_id.provision_account.name,
                                        'credit': (
                                                          product_price * provision.percentage_value) * new_line.purchase_line_id.qty_received,
                                        'move_id': new_line.account_move_ids.invoice_line_ids.move_id.id})]})
                        provisions_debit = 0
                        for provision in provisions:
                            provisions_debit = provisions_debit + ((
                                                                           product_price * provision.percentage_value) * new_line.purchase_line_id.qty_received)

                        debit_dict['debit'] = provisions_debit
                        new_line.account_move_ids.write({'invoice_line_ids': [(0, 0, debit_dict)]})

                        if new_line.purchase_line_id and new_line.purchase_line_id.provision_ids and not new_line.purchase_line_id.quantity_set:
                            new_line.purchase_line_id.update({
                                'price_unit': product_price,
                                'quantity_set': True,
                                'provisioned': False,
                            })

        return result


class StockMove(models.Model):
    _inherit = "stock.move"

    provisioned = fields.Boolean(default=False)


class AccountMove(models.Model):
    _inherit = "account.move"

    @contextmanager
    def _check_balanced(self, container):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
            yield
            if disabled:
                return

        unbalanced_moves = self._get_unbalanced_moves(container)
        if self.stock_move_id.purchase_line_id.provision_ids:
            pass
        else:
            if unbalanced_moves:
                error_msg = _("An error has occurred.")
                for move_id, sum_debit, sum_credit in unbalanced_moves:
                    move = self.browse(move_id)
                    error_msg += _(
                        "\n\n"
                        "The move (%s) is not balanced.\n"
                        "The total of debits equals %s and the total of credits equals %s.\n"
                        "You might want to specify a default account on journal \"%s\" to automatically balance each move.",
                        move.display_name,
                        format_amount(self.env, sum_debit, move.company_id.currency_id),
                        format_amount(self.env, sum_credit, move.company_id.currency_id),
                        move.journal_id.name)
                raise UserError(error_msg)
