# # -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
import werkzeug
import datetime
import simplejson
from openerp.addons.website_mobile.website_mobile import mobile_crud

import logging
_logger = logging.getLogger(__name__)

#~ MODULE_BASE_PATH = request.env.ref('mobile_timereport_menu').url
MOBILE_BASE_PATH = '/mobile/timereport/'
#~ MODULE_TITLE = _('My tasks')

class mobile_timereport(mobile_crud, http.Controller):
    _name = 'mobile.timereport'

    def __init__(self):
        super(mobile_timereport, self).__init__()
        self.search_domain = [('date_start', '<', fields.Datetime.now())]
        self.model = 'project.task'
        self.load_fields(['name', 'project_id', 'planned_hours', 'stage_id']) # help for description doesn't work
        self.root = MOBILE_BASE_PATH
        self.title = _('Task')

    @http.route([MOBILE_BASE_PATH, MOBILE_BASE_PATH+'<model("project.task"):task>'],type='http', auth="user", website=True)
    def task_list(self, task=None, search='', **post):
        self.search_domain.append(('user_id', '=', request.uid))
        return self.do_list(obj=task)

    @http.route([MOBILE_BASE_PATH+'<string:search>/search', MOBILE_BASE_PATH+'search'],type='http', auth="user", website=True)
    def task_search(self, search=None, **post):
        return self.do_list(search=search or post.get('search_words'))

    @http.route([MOBILE_BASE_PATH+'<model("project.task"):task>/edit'],type='http', auth="user", website=True)
    def task_edit(self, task=None, search='', **post):
        return self.do_edit(obj=task,**post)

    @http.route([MOBILE_BASE_PATH+'<model("project.task"):task>/delete'],type='http', auth="user", website=True)
    def task_delete(self, task=None, search='', **post):
        return self.do_delete(obj=task, base_path=MOBILE_BASE_PATH)


class mobile_timereport_work(mobile_crud, http.Controller):
    _name = 'mobile.timereport.work'

    def __init__(self):
        super(mobile_timereport_work, self).__init__()
        #~ self.search_domain = [('task_id', '=', None)]
        self.model = 'project.task.work'
        self.load_fields(['id', 'name', 'hours', 'date', 'user_id', 'task_id'])
        for f in self.fields_info:
            if f.name == 'task_id' or f.name == 'date' or f.name == 'id':
                f.type = 'hidden'
            if f.name == 'id':
                f.write = False
        self.root = MOBILE_BASE_PATH+'work/'
        self.title = _('Work')
        self.col_size_edit = '4'
        self.col_size_view = '12'

    @http.route([MOBILE_BASE_PATH+'work/add'],type='http', auth="user", website=True)
    def work_add(self, task=None, search='',**post):
        return self.do_add(**post)

    @http.route([MOBILE_BASE_PATH+'work/<model("project.task.work"):work>', MOBILE_BASE_PATH+'<model("project.task"):task>/works'],type='http', auth="user", website=True)
    def work_list(self, task=None, work=None, search='', **post):
        if task:
            domain = [('task_id', '=', task.id)]
        else:
            domain = None
        return self.do_list(obj=work, domain=domain)

    @http.route([MOBILE_BASE_PATH+'work/<model("project.task.work"):work>/edit'],type='http', auth="user", website=True)
    def work_edit(self, work=None, search='', **post):
        return self.do_edit(obj=work,**post)

    @http.route([MOBILE_BASE_PATH+'<model("project.task"):task>/works/edit_grid'],type='http', auth="user", website=True)
    def work_edit_grid(self, task=None, search='', **post):
        if task:
            return self.do_grid(obj_ids=task.work_ids)

    @http.route([MOBILE_BASE_PATH+'work/<model("project.task.work"):work>/delete'],type='http', auth="user", website=True)
    def work_delete(self, work=None, search='', **post):
        return self.do_delete(obj=work, base_path=MOBILE_BASE_PATH+'%s' %work.task_id.id)


    # time report
    #~ def do_report(self,obj=None, base_path='/', **post):
        #~ if request.httprequest.method == 'GET':
            #~ return request.render(template['detail'], {'crud': self, 'object': obj, 'root': base_path, 'title': obj.name, 'mode': 'report'})
        #~ else:
            #~ try:
                #~ self.validate_form()
            #~ except Exception as e:
                #~ return request.render(self.template['detail'], {'crud': self, 'object': obj, 'title': obj.name, 'mode': 'report'})
            #~ else:
                #~ try:
                    #~ work = request.env['project.task.work'].create({
                        #~ 'task_id': task.id,
                        #~ 'name': post.get('worked_desc'),
                        #~ 'hours': float(post.get('worked_hours')),
                        #~ 'date': fields.Datetime.now(),
                        #~ 'user_id': request.uid,
                    #~ })
                    #~ request.context['alerts']=[{'subject': _('Saved'),'message':_('Time report successful'),'type': 'success'}]
                    #~ return request.render(self.template['detail'], {'crud': self, 'object': obj, 'title': obj.name, 'mode': 'report'})
                #~ except: # Catch exception message
                    #~ request.context['alerts']=[{'subject': _('Error'),'message':_('Time report failed'),'type': 'error'}]
                    #~ return request.render(self.template['detail'], {'crud': self, 'object': obj, 'title': obj.name, 'mode': 'report'})

    #~ @http.route([
    #~ MODULE_BASE_PATH,
    #~ MODULE_BASE_PATH + '<model("project.task"):task>',
    #~ MODULE_BASE_PATH + '<model("project.task"):task>/report',
    #~ MODULE_BASE_PATH + '<model("project.task"):task>/edit',
    #~ MODULE_BASE_PATH + '<model("project.task"):task>/delete',
    #~ MODULE_BASE_PATH + 'search',
    #~ ], type='http', auth='user', website=True)
    #~ def get_task(self, task=None, search='', **post):
        #~ search_domain = [('user_id', '=', request.uid), ('date_start', '<', fields.Datetime.now())]
        #~ model = 'project.task'
        #~ fields_list =  ['name', 'project_id', 'description', 'planned_hours', 'stage_id']
        #~ template = {'list': 'mobile_project_timereport.object_list', 'detail': 'mobile_project_timereport.object_detail'}

        #~ if request.httprequest.url[-4:] == 'edit': #Edit
            #~ if request.httprequest.method == 'GET':
                #~ return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': task.name, 'db': request.db, 'mode': 'edit'})
            #~ else:
                #~ values = {}
                #~ for field in fields_list:
                    #~ field_type = request.env[model].fields_get([field])[field]['type']
                    #~ if field_type == 'many2one':
                        #~ values[field] = int(post.get(field))
                    #~ elif field_type == 'one2many':
                        #~ pass
                    #~ elif field_type == 'many2many':
                        #~ pass
                    #~ else:
                        #~ values[field] = post.get(field)
                #~ task.write(values)
                #~ return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': task.name, 'db': request.db, 'mode': 'view'})
        #~ elif request.httprequest.url[-6:] == 'report': #Report
            #~ if request.httprequest.method == 'GET':
                #~ return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': 'Time Report', 'db': request.db, 'mode': 'report'})
            #~ else:
                #~ work = request.env['project.task.work'].create({
                    #~ 'task_id': task.id,
                    #~ 'name': post.get('worked_desc'),
                    #~ 'hours': float(post.get('worked_hours')),
                    #~ 'date': fields.Datetime.now(),
                    #~ 'user_id': request.uid,
                #~ })
                #~ return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': post.get('worked_hours') + ' hours reported', 'db': request.db, 'mode': 'view'})
        #~ if request.httprequest.url[-6:] == 'search': #Search
            #~ if request.httprequest.method == 'POST':
                #~ search = post.get('search_words')
            #~ search_domain.append(('name', 'ilike', search))
        #~ elif task:  # Detail
            #~ return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': 'Time Report', 'db': request.db, 'mode': 'view'})
        #~ return request.render(template['list'], {
            #~ 'objects': request.env[model].search(search_domain, order='date_start desc'),
            #~ 'title': MODULE_TITLE,
            #~ 'root': MODULE_BASE_PATH,
            #~ 'db': request.db,
        #~ })
