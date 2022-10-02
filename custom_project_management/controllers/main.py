# -*- coding: utf-8 -*-

from openerp.addons.web import http
from openerp.http import request
from openerp.addons.website.controllers.main import Website


class Website(Website):

	@http.route('/page/task', type='http', auth="public", website=True)
	def website_page_task(self):
		task_obj = request.env()['project.task'].sudo()
		cr = request.cr
		cr.execute('SELECT t.id,t.name,t.user_image,t.project_id,t.user_id,p.analytic_account_id,u.partner_id,rp.name,aa.name FROM project_task t, project_project p, res_users u, res_partner rp, account_analytic_account aa WHERE t.project_id = p.id AND t.user_id = u.id AND u.partner_id = rp.id AND p.analytic_account_id = aa.id')
		data = cr.fetchall()
		vals = [{'user_name': str(d[7]), 'user_image': d[2], 'task_name': str(d[1]), 'project_name': str(d[8])} for d in data]
		return request.render('custom_project_management.page_task', {'tasks': vals})