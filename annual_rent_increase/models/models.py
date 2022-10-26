# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

# from dateutil.relativedelta import relativedelta



#
# class NewModule(models.TransientModel):
#     _inherit ='sale.advance.payment.inv'
#
#     def create_invoices(self):
#         res=super(NewModule, self).create_invoices()
#         for rec in self:
#             print('sale_orders',sale_orders)
#             sale_orders.compute_lines()
#         return res





class AnnualIncrease(models.Model):
    _name = 'annual.increase'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char(string="Name", required=False,related='sale_id.name' )
    date = fields.Date(string="Date", required=True, )
    percent = fields.Float(string="Percent %", required=False, compute='get_percent')
    amount = fields.Float(string="Amount", required=False,)
    # compute='get_amount')
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('posted', 'Posted'), ], required=False, )
    sale_id = fields.Many2one(comodel_name="sale.order", string="Sale", required=False, )


    # @api.depends('percent','sale_id.amount_total')
    # def get_amount(self):
    #     for rec in self:
    #         # pass
    #         annual_increase=self.env['annual.increase'].sudo().search([('sale_id','=',rec.sale_id.id),('date','<',rec.date)])
    #         print('annual_increase',annual_increase)
    #         amount_annual_increase = sum(annual_increase.mapped('amount'))
    #         print('amount_annual_increase',amount_annual_increase)
    #         rec.amount = False
    #         rec.amount = rec.percent * (rec.sale_id.amount_total + amount_annual_increase) / 100

    @api.depends('amount', 'sale_id.amount_total')
    def get_percent(self):
        for rec in self:
            # pass
            annual_increase = self.env['annual.increase'].sudo().search(
                [('sale_id', '=', rec.sale_id.id), ('date', '<', rec.date)])
            print('annual_increase', annual_increase)
            amount_annual_increase = sum(annual_increase.mapped('amount'))
            print('amount_annual_increase', amount_annual_increase)
            rec.percent = False
            if rec.sale_id.amount_total + amount_annual_increase > 0:
                rec.percent = (rec.amount / (rec.sale_id.amount_total + amount_annual_increase)) * 100
            else:
                rec.percent = False


class AccountMove(models.Model):
    _inherit = 'account.move'



    sale_annual_id = fields.Many2one(comodel_name="sale.order", string="", required=False, )



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    annual_increase_ids = fields.One2many(comodel_name="annual.increase", inverse_name="sale_id", string="", required=False, )


    date_from = fields.Date(string="Date From", required=False,default=fields.Date.today() )
    date_to = fields.Date(string="Date To", required=False, )





    def button_sale_journal_entry(self):
        annual_increases=self.env['annual.increase'].sudo().search([('state','=','draft'),('date','<',fields.Date.today())])
        print('annual_increases',annual_increases)
        for annual_increase in annual_increases:
            data=[]
            if annual_increase.sale_id.invoice_ids :
                journal=annual_increase.sale_id.invoice_ids[0].journal_id
                data.append([0,0,{
                    'name': 'annual increase',
                    'quantity': 1,
                    'price_unit': annual_increase.amount,
                }])
                invoice = self.env['account.move'].sudo().create({
                    'move_type': 'out_invoice',
                    'ref': annual_increase.name,
                    'date': annual_increase.date,
                    'journal_id': journal.id,
                    'sale_annual_id': annual_increase.sale_id.id,
                    'partner_id': annual_increase.sale_id.partner_id.id,
                    'invoice_line_ids' : data,
                    # 'line_ids': [(0, 0, {
                    #     'account_id': annual_increase.sale_id.partner_id.property_account_receivable_id.id,
                    #     # 'partner_id': annual_increase.sale_id.partner_id.id,
                    #     # 'name': rec.employee_id.name,
                    #     'debit': annual_increase.amount,
                    # }), (0, 0, {
                    #     'account_id': journal.default_account_id.id,
                    #     # 'partner_id': rec.employee_id.id,
                    #     'name': 'Annual Increase',
                    #     'credit': annual_increase.amount,
                    # })],
                })
                print('invoice',annual_increase.sale_id.invoice_ids)
                annual_increase.sale_id.invoice_ids = [(4, invoice.id)]
                print('invoice_D',annual_increase.sale_id.invoice_ids)
                annual_increase.state = 'posted'


    def get_annual_invoice(self):
        for rec in self:
            return {
                'name': 'Invoices',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('sale_annual_id', '=', self.id)],
            }




    @api.onchange('date_from','date_to','amount_total')
    def compute_lines(self):
        for rec in self:
            rec.annual_increase_ids = False
            data=[]
            if rec.date_from and rec.date_to:
                delta = relativedelta(rec.date_to, rec.date_from)
                date_years = delta.years
                date_months = delta.months
                date_days = delta.days
                print('date_years',date_years)
                print('date_months',date_months)
                print('date_days',date_days)
                if date_years >= 1 :
                    print('rrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
                    num=0
                    for x in range(1,date_years+1):
                        print('x',x)
                        data.append([0,0,{
                            'date': rec.date_from + relativedelta(years=x),
                            # 'date': rec.date_from + + datetime.timedelta(years=1),
                            'state': 'draft',

                        }])
                        num=x
                    if date_months >= 1 and num >=1:
                        data.append([0, 0, {
                            'date': rec.date_from + relativedelta(years=num+1),
                            'state': 'draft',

                        }])
                rec.annual_increase_ids = data
