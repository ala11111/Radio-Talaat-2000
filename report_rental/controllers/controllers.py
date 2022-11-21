# -*- coding: utf-8 -*-
# from odoo import http


# class ReportRental(http.Controller):
#     @http.route('/report_rental/report_rental', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_rental/report_rental/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_rental.listing', {
#             'root': '/report_rental/report_rental',
#             'objects': http.request.env['report_rental.report_rental'].search([]),
#         })

#     @http.route('/report_rental/report_rental/objects/<model("report_rental.report_rental"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_rental.object', {
#             'object': obj
#         })
