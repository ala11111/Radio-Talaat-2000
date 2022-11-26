# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerDueWizard(models.TransientModel):
    _name = 'customer.due.wizard'
    _description = 'Customer Due Wizard'

    name = fields.Char()
    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date To", required=False, )
    partner_ids = fields.Many2many('res.partner', string='customer', domain=[('customer_rank', '>', 0)])

    def export_product(self):
        for rec in self:
            if not rec.partner_ids:
                rec.partner_ids = self.env['res.partner'].sudo().search([('customer_rank', '>', 0)]).ids
            return self.env.ref('report_rental.report_action_id_customer_due').report_action(self)


# customer_due
class customer_due(models.AbstractModel):
    _name = 'report.report_rental.customer_due'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'customer_due'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet('General Ledger Report')
            format0 = workbook.add_format({'font_size': 15, 'align': 'center'})
            format1 = workbook.add_format(
                {'font_size': 15, 'align': 'center', 'bold': True, 'bg_color': '#D5D5D5', 'color': 'black',
                 'border': 2})
            format2 = workbook.add_format(
                {'font_size': 11, 'align': 'center', 'bold': True,
                 'border': 5})
            format10 = workbook.add_format({'align': 'center', 'bold': True, 'bg_color': '#FF6600', 'border': 5})
            format3 = workbook.add_format(
                {'font_size': 13,'align': 'center', 'bold': True, 'bg_color': '#E7DAD8', 'color': 'black', 'border': 5})
            row = 1
            if obj.partner_ids:
                print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                sheet.write(row, 1, 'القيمه', format3)
                sheet.set_column(row, 1, 30)
                sheet.set_column(row, 2, 30)
                sheet.set_column(row, 3, 30)
                sheet.set_column(row, 4, 30)
                sheet.set_row(row, 20)
                sheet.write(row, 2, 'اقرب استحقاق', format3)
                sheet.write(row, 3, 'رقم امر البيع', format3)
                sheet.write(row, 4, 'اسم العميل ', format3)
                row+=1
                for partner in obj.partner_ids:
                    rental = self.env['rental.details'].sudo().search(
                        [('partner_id', '=', partner.id), ('state', '!=', 'yes'), ('date', '>=', obj.date_from),
                         ('date', '<=', obj.date_to)], order="date",limit=1)

                    if rental:
                        rental_plus = self.env['rental.details'].sudo().search(
                            [('partner_id', '=', partner.id), ('state', '!=', 'yes'), ('date', '=', rental.date)])

                        sheet.write(row, 1,sum(rental_plus.mapped('net')) , format2)
                        # sheet.set_column(row, 1, 30)
                        # sheet.set_row(row, 20)
                        sheet.write(row, 2, str(rental.date), format2)
                        sheet.write(row, 3, rental.sale_id.name, format2)
                        sheet.write(row, 4, partner.name, format2)
                        row+=1

