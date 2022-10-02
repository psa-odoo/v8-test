# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _


class project_task(osv.osv):
    _inherit = 'project.task'

    _columns = {
        'user_image': fields.related('user_id', 'image', type="binary", readonly=True, string="User Image", store=True,),
    }


class project_project(osv.osv):
    _inherit = 'project.project'

    def _open_task_count(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        not_open_task = [self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_merge')[1], self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_deployment')[1], self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_cancel')[1]]
        for tasks in self.browse(cr, uid, ids, dict(context, active_test=False)):
            res[tasks.id] = len(tasks.task_ids.filtered(lambda t: t.stage_id.id not in not_open_task))
        return res

    def _delay_task_count(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for tasks in self.browse(cr, uid, ids, dict(context, active_test=False)):
            res[tasks.id] = len(tasks.task_ids.filtered(lambda t: t.date_deadline and t.date_deadline < datetime.today().strftime('%Y-%m-%d')))
        return res

    def _current_month_finish_task_count(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        domain = [('date_end','>=',datetime.today().strftime('%Y-%m') + '-01 00:00:00'),
            ('date_end','<',(datetime.today()+relativedelta(months=1)).strftime('%Y-%m') + '-01 00:00:00'),
            ('stage_id', 'in', [self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_deployment')[1], self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_merge')[1]]),
        ]
        for tasks in self.browse(cr, uid, ids, dict(context, active_test=False)):
            res[tasks.id] = len(self.pool.get('project.task').search(cr, uid, domain + [('project_id', '=', tasks.id)]))
        return res

    def _past_week_finish_task_count(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        domain = [('date_end', '<=', ((datetime.today()+relativedelta(weeks=0, weekday=-1)).strftime('%Y-%m-%d 23:59:59'))),
            ('date_end', '>=', ((datetime.today()-relativedelta(weeks=1, weekday=0)).strftime('%Y-%m-%d 00:00:00'))),
            ('stage_id', 'in', [self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_deployment')[1], self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_merge')[1]]),
        ]
        for tasks in self.browse(cr, uid, ids, dict(context, active_test=False)):
            res[tasks.id] = len(self.pool.get('project.task').search(cr, uid, domain + [('project_id', '=', tasks.id)]))
        return res

    _columns = {
        'open_task_count': fields.function(_open_task_count, type='integer', string="Open Tasks",),
        'delay_task_count': fields.function(_delay_task_count, type='integer', string="Delay Tasks",),
        'current_month_finish_task': fields.function(_current_month_finish_task_count, type='integer', string="Current Month Finish Task",),
        'past_week_finish_task': fields.function(_past_week_finish_task_count, type='integer', string="Past week Finish Task",),
    }

    def open_task_tree_view(self, cr, uid, ids, context):
        not_open_task = [self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_merge')[1], self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_deployment')[1], self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_cancel')[1]]
        domain = [('project_id', 'in', ids), ('stage_id', 'not in', not_open_task)]
        task_ids = self.pool.get('project.task').search(cr, uid, domain)
        
        return {
            'name': _('Open Task'),
            'domain': domain,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'limit': 80,
        }

    def delay_task_tree_view(self, cr, uid, ids, context):
        domain = [('project_id', 'in', ids), ('date_deadline', '<', datetime.today().strftime('%Y-%m-%d'))]
        task_ids = self.pool.get('project.task').search(cr, uid, domain)
        
        return {
            'name': _('Delay Task'),
            'domain': domain,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'limit': 80,
        }

    def current_month_finish_task_tree_view(self, cr, uid, ids, context):
        domain = [('date_end','>=',datetime.today().strftime('%Y-%m') + '-01 00:00:00'),
            ('date_end','<',(datetime.today()+relativedelta(months=1)).strftime('%Y-%m') + '-01 00:00:00'),
            ('stage_id', 'in', [self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_deployment')[1], self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_merge')[1]]),
            ('project_id', 'in', ids),
        ]
        task_ids = self.pool.get('project.task').search(cr, uid, domain)
        return {
            'name': _('Current Month Finish Task'),
            'domain': domain,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'limit': 80,
        }

    def past_week_finish_task_tree_view(self, cr, uid, ids, context):
        domain = [('date_end', '<=', ((datetime.today()+relativedelta(weeks=0, weekday=-1)).strftime('%Y-%m-%d 23:59:59'))),
            ('date_end', '>=', ((datetime.today()-relativedelta(weeks=1, weekday=0)).strftime('%Y-%m-%d 00:00:00'))),
            ('stage_id', 'in', [self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_deployment')[1], self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'project_tt_merge')[1]]),
            ('project_id', 'in', ids),
        ]
        task_ids = self.pool.get('project.task').search(cr, uid, domain)
        
        return {
            'name': _('Current Week Finish Task'),
            'domain': domain,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'limit': 80,
        }