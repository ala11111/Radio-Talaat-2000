# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil import relativedelta

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_service = fields.Boolean(string="Is Service",  )



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pay_method = fields.Integer(string="سياسه الدفع", required=False,default=1 )



    def action_confirm(self):
        res=super(SaleOrder, self).action_confirm()
        for rec in self:
            for line in rec.order_line:
                if not line.product_id.is_service and line.product_id.rent_ok:
                    date_month = 0
                    months = 0
                    month_increase = 0
                    delta = relativedelta.relativedelta(line.return_date, line.pickup_date)
                    date_month = delta.months + (delta.years * 12)
                    print('date_month',date_month)
                    print('date_month',type(date_month))
                    months=int(date_month / rec.pay_method)

                    print('months',months)

                    if months > 0:
                        for month in range(0, months):
                            print(True)
                            rental_details = self.env['rental.details'].sudo().create({
                                'name':line.product_id.name,
                                'date':line.pickup_date+relativedelta.relativedelta(months=month_increase),
                                'sale_id':rec.id,
                                'partner_balance':900,
                                'product_id':line.product_id.id,
                                'product_amount':line.price_subtotal / months ,
                                'service':sum(rec.order_line.filtered(lambda l: l.product_id.is_service == True).mapped('price_subtotal')) / months ,
                            })
                            month_increase+=1
        return res








class RentalDetails(models.Model):
    _name = 'rental.details'
    _rec_name = 'name'
    _description = 'Rental Details'

    name = fields.Char(string="Name", required=False, )
    date = fields.Date(string="تاريخ الاستحقاق", required=False, )
    sale_id = fields.Many2one(comodel_name="sale.order", string="أمر البيغ", required=False, )
    currency_id = fields.Many2one(comodel_name="res.currency", string="العمله", required=False,related='sale_id.currency_id',store=True )
    partner_id = fields.Many2one(comodel_name="res.partner", string="العميل", required=False,related='sale_id.partner_id' ,store=True)
    partner_balance = fields.Float(string="رصيد العميل",  required=False,compute='git_Previous_customer_balance' )
    product_id = fields.Many2one(comodel_name="product.product", string="المنتج", required=False, )
    product_amount = fields.Float(string="قيمه الايجار",  required=False, )
    service = fields.Float(string="الصيانه",  required=False, )
    customer_due = fields.Float(string="اجمالي المستحق المستحق علي العميل",  required=False,compute='get_customer_due', store=True )
    discount = fields.Float(string="تخفيض / علاوه",  required=False, )
    discount_reason = fields.Text(string="سبب العلاوه/التخفيض", required=False, )
    net = fields.Float(string="الصافي",  required=False, compute='get_customer_due', store=True)
    state = fields.Selection(string="حاله التحصيل", selection=[('yes', 'نعم'), ('no', 'لا'),('partial', 'جزئي') ], required=False, )
    reason = fields.Text(string="السبب", required=False, )




    @api.depends('partner_id')
    def git_Previous_customer_balance(self):
        for rec in self:
            balance=0
            account_move_lines_balance = self.env['account.move.line'].sudo().search([
                ('partner_id', '=', rec.partner_id.id),
                ('move_id.state', '=', 'posted'),
                ('account_id.user_type_id', 'in', [self.env.ref('account.data_account_type_receivable').id,
                                                  self.env.ref('account.data_account_type_payable').id]),
            ], order="date")
            print('account_move_lines_balance',account_move_lines_balance)
            for move_balance in account_move_lines_balance:
                balance = balance + move_balance.debit - move_balance.credit
            rec.partner_balance=balance






    @api.depends('product_amount','service','discount')
    def get_customer_due(self):
        for rec in self:
            rec.customer_due = rec.product_amount + rec.service
            rec.net = rec.customer_due - rec.discount



    @api.onchange('sale_id','partner_id','product_id','date')
    def get_name_rental(self):
        for rec in self:
            rec.name = str(rec.sale_id.name)+'-'+str(rec.partner_id.name)+'-'+str(rec.product_id.name)+'-'+str(rec.date)
