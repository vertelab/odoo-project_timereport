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

import logging
_logger = logging.getLogger(__name__)

#~ MODULE_BASE_PATH = request.env.ref('mobile_timereport_menu').url
MODULE_BASE_PATH = '/mobile/timereport/'
MODULE_TITLE = _('My tasks')

class mobile_timereport(http.Controller):
    @http.route([
    MODULE_BASE_PATH,
    MODULE_BASE_PATH + '<model("project.task"):task>',
    MODULE_BASE_PATH + '<model("project.task"):task>/report',
    MODULE_BASE_PATH + '<model("project.task"):task>/edit',
    MODULE_BASE_PATH + '<model("project.task"):task>/delete',
    MODULE_BASE_PATH + 'search',
    ], type='http', auth='user', website=True)
    def get_task(self, task=None, search='', **post):
        search_domain = [('user_id', '=', request.uid), ('date_start', '<', fields.Datetime.now())]
        model = 'project.task'
        fields_list =  ['name', 'project_id', 'description', 'planned_hours', 'stage_id']
        template = {'list': 'mobile_project_timereport.object_list', 'detail': 'mobile_project_timereport.object_detail'}

        if request.httprequest.url[-4:] == 'edit': #Edit
            if request.httprequest.method == 'GET':
                return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': task.name, 'db': request.db, 'mode': 'edit'})
            else:
                values = {}
                for field in fields_list:
                    field_type = request.env[model].fields_get([field])[field]['type']
                    if field_type == 'many2one':
                        values[field] = int(post.get(field))
                    elif field_type == 'one2many':
                        pass
                    elif field_type == 'many2many':
                        pass
                    else:
                        values[field] = post.get(field)
                task.write(values)
                return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': task.name, 'db': request.db, 'mode': 'view'})
        elif request.httprequest.url[-6:] == 'report': #Report
            if request.httprequest.method == 'GET':
                return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': 'Time Report', 'db': request.db, 'mode': 'report'})
            else:
                work = request.env['project.task.work'].create({
                    'task_id': task.id,
                    'name': post.get('worked_desc'),
                    'hours': float(post.get('worked_hours')),
                    'date': fields.Datetime.now(),
                    'user_id': request.uid,
                })
                return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': post.get('worked_hours') + ' hours reported', 'db': request.db, 'mode': 'view'})
        if request.httprequest.url[-6:] == 'search': #Search
            if request.httprequest.method == 'POST':
                search = post.get('search_words')
            search_domain.append(('name', 'ilike', search))
        elif task:  # Detail
            return request.render(template['detail'], {'model': model, 'object': task, 'fields': fields_list, 'root': MODULE_BASE_PATH, 'title': 'Time Report', 'db': request.db, 'mode': 'view'})
        return request.render(template['list'], {
            'objects': request.env[model].search(search_domain, order='date_start desc'),
            'title': MODULE_TITLE,
            'root': MODULE_BASE_PATH,
            'db': request.db,
        })
