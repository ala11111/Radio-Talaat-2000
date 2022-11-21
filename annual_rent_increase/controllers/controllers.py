# -*- coding: utf-8 -*-
# from odoo import http


# class AnnualRentIncrease(http.Controller):
#     @http.route('/annual_rent_increase/annual_rent_increase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/annual_rent_increase/annual_rent_increase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('annual_rent_increase.listing', {
#             'root': '/annual_rent_increase/annual_rent_increase',
#             'objects': http.request.env['annual_rent_increase.annual_rent_increase'].search([]),
#         })

#     @http.route('/annual_rent_increase/annual_rent_increase/objects/<model("annual_rent_increase.annual_rent_increase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('annual_rent_increase.object', {
#             'object': obj
#         })
