# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil import relativedelta

class apartment_state(models.Model):
    _name = 'apartment.state'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char()



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_service = fields.Boolean(string="Is Service", )

    is_sales_use = fields.Boolean(string="Sales Use",compute='get_is_sales_use' ,store=True )
    is_sales = fields.Boolean(string="",  )
    new_field_ids = fields.Many2many(comodel_name="", relation="", column1="", column2="", string="", )
    partner_ids = fields.Many2many('res.partner',relation="partner_ids", string='Owners', domain=[('customer_rank', '>', 0)])
    sales_person_ids = fields.Many2many('res.partner',relation="sales_person_ids", string='Sale Persons')
    tax_position = fields.Selection(string="Tax Position", selection=[('registered', 'Registered'), ('unregistered', 'Unregistered'),('under_registration', 'Under Registration'), ], required=False, )
    land_space = fields.Float(string="Land Space",  required=False, )
    real_estate_space = fields.Float(string="Real Estate Space",  required=False, )
    number_of_floors = fields.Float(string="Number of Floors",  required=False, )
    apartment_description = fields.Text(string="Apartment Description", required=False, )
    apartment_state_id = fields.Many2one(comodel_name="apartment.state", string="Apartment State", required=False, )
    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account", required=False, )
    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag", string="analytic tags"
    )



    @api.depends('name')
    def get_is_sales_use(self):
        for rec in self:
            sales_line=self.env['sale.order.line'].sudo().search([('product_id','=',rec.product_variant_id.id),('order_id.state','in',['sale','done'])])
            if sales_line :
                rec.is_sales_use = True
            else:
                rec.is_sales_use = False





class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'order_id.date_order', 'order_id.partner_id')
    def _compute_analytic_tag_ids(self):
        for line in self:
            # if not line.display_type and line.state == 'draft':
            #     default_analytic_account = line.env['account.analytic.default'].sudo().account_get(
            #         product_id=line.product_id.id,
            #         partner_id=line.order_id.partner_id.id,
            #         user_id=self.env.uid,
            #         date=line.order_id.date_order,
            #         company_id=line.company_id.id,
            #     )
            #     line.analytic_tag_ids = default_analytic_account.analytic_tag_ids
            line.analytic_tag_ids = line.product_id.analytic_tag_ids.ids




class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pay_method = fields.Integer(string="Payment Terms", required=False, default=1)
    payment_method_select = fields.Selection(string="Payment Method", selection=[('cash', 'Cash'), ('check', 'Check'),('bank_transfer', 'Bank Transfer'), ], required=False, )
    lessor_ids = fields.Many2many2one(comodel_name="res.partner", string="Lessors", required=False, )

    def action_draft(self):
        res=super(SaleOrder, self).action_draft()
        rental_details = self.env['rental.details'].sudo().search([('sale_id','=',self.id)]).sudo().unlink()
        return res



    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            service_value = 0
            service = rec.order_line.filtered(lambda l: l.product_id.is_service == True)
            if service:
                print('service',service)
                months_service = int((relativedelta.relativedelta(service.return_date, service.pickup_date).months + (
                            (relativedelta.relativedelta(service.return_date, service.pickup_date).years) * 12))/ rec.pay_method) + 1
                service_value=service.price_subtotal / months_service
                print('service_value',service_value)
            for line in rec.order_line:
                line.product_id.is_sales_use = True
                if not line.product_id.is_service and line.product_id.rent_ok:
                    date_month = 0
                    months = 0
                    month_increase = 0
                    delta = relativedelta.relativedelta(line.return_date, line.pickup_date)
                    date_month = delta.months + (delta.years * 12)
                    months = int(date_month / rec.pay_method) + 1
                    if months > 0:
                        for month in range(0, months):
                            date = line.pickup_date + relativedelta.relativedelta(months=month_increase)
                            rental_details = self.env['rental.details'].sudo().create({
                                'name': line.product_id.name,
                                'date': date,
                                'sale_id': rec.id,
                                # 'partner_balance':900,
                                'product_id': line.product_id.id,
                                'product_amount': line.price_subtotal / months,
                                'service': service_value if service and date >= service.pickup_date and date <= service.return_date else 0,
                            })
                            month_increase += rec.pay_method
        return res


class RentalDetails(models.Model):
    _name = 'rental.details'
    _rec_name = 'name'
    _description = 'Rental Details'

    name = fields.Char(string="Name", required=False, )
    date = fields.Date(string="تاريخ الاستحقاق", required=False, )
    sale_id = fields.Many2one(comodel_name="sale.order", string="Sale Order", required=False, )
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", required=False,
                                  related='sale_id.currency_id', store=True)
    partner_id = fields.Many2one(comodel_name="res.partner", string="renter", required=False,
                                 related='sale_id.partner_id', store=True)
    partner_balance = fields.Float(string="renter Balance", required=False, compute='git_Previous_customer_balance')
    product_id = fields.Many2one(comodel_name="product.product", string="Item", required=False, )
    product_amount = fields.Float(string="Rent Value", required=False, )
    service = fields.Float(string="Service", required=False, )
    customer_due = fields.Float(string="renter Due", required=False, compute='get_customer_due',
                                store=True)
    discount = fields.Float(string="Discount", required=False, )
    discount_reason = fields.Text(string="Discount Reason", required=False, )
    net = fields.Float(string="Net", required=False, compute='get_customer_due', store=True)
    state = fields.Selection(string="Collection State", selection=[('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')],
                             required=False, )
    reason = fields.Text(string="Reason", required=False, )

    def button_send_notify_rental_report_id(self):
        today = fields.Date.today()
        for rec in self.search([('state','!=','yes')]):
            if rec.date and  today + relativedelta.relativedelta(days=2) == rec.date or today == rec.date or today >= rec.date:
                print('ssssssssssssssssssssss')
                body = '<a target=_BLANK href="/web?#id=' + str(
                    rec.id) + '&view_type=form&model=rental.details&action=" style="font-weight: bold">' + str(
                    rec.name) + '</a>'
                partners = [x.partner_id.id for x in self.env.ref('report_rental.rental_notify_id').users]
                # partners = [rec.project_id.user_id.partner_id.id]
                if partners:
                    thread_pool = self.env['mail.thread']
                    thread_pool.sudo().message_notify(
                        partner_ids=partners,
                        subject="Customer "+str(rec.partner_id.name)+" Has Rental " + str(rec.name) + " need to collection in "+ str(rec.date),
                        body="Message:Customer "+str(rec.partner_id.name)+" Has Rental " + str(body) + " need to collection in "+ str(rec.date),
                        email_from=self.env.user.company_id.email)
    @api.depends('partner_id')
    def git_Previous_customer_balance(self):
        for rec in self:
            balance = 0
            account_move_lines_balance = self.env['account.move.line'].sudo().search([
                ('partner_id', '=', rec.partner_id.id),
                ('move_id.state', '=', 'posted'),
                ('account_id.user_type_id', 'in', [self.env.ref('account.data_account_type_receivable').id,
                                                   self.env.ref('account.data_account_type_payable').id]),
            ], order="date")
            # print('account_move_lines_balance', account_move_lines_balance)
            for move_balance in account_move_lines_balance:
                balance = balance + move_balance.debit - move_balance.credit
            rec.partner_balance = balance

    @api.depends('product_amount', 'service', 'discount')
    def get_customer_due(self):
        for rec in self:
            rec.customer_due = rec.product_amount + rec.service
            rec.net = rec.customer_due + rec.discount

    @api.onchange('sale_id', 'partner_id', 'product_id', 'date')
    def get_name_rental(self):
        for rec in self:
            rec.name = str(rec.sale_id.name) + '-' + str(rec.partner_id.name) + '-' + str(
                rec.product_id.name) + '-' + str(rec.date)
