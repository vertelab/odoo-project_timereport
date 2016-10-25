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
        self.load_fields(['name', 'project_id', 'planned_hours', 'stage_id', 'work_ids'])
        for f in self.fields_info:
            if f.name == 'work_ids':
                f.child_class = mobile_timereport_work()
        self.root = MOBILE_BASE_PATH
        self.title = _('Task')

    @http.route([MOBILE_BASE_PATH, MOBILE_BASE_PATH+'<model("project.task"):task>'],type='http', auth="user", website=True)
    def task_list(self, task=None, search='', **post):
        self.search_domain.append(('user_id', '=', request.uid))
        return self.do_list(obj=task, template_detail='mobile_project_timereport.layout_extend_timereport')

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
        self.load_fields(['name', 'hours', 'date', 'user_id', 'task_id'])
        for f in self.fields_info:
            if f.name == 'task_id' or f.name == 'date':
                f.type = 'hidden'
        self.root = MOBILE_BASE_PATH+'work/'
        self.title = _('Work')
        self.col_size_edit = '4'
        self.col_size_view = '4'

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

    @http.route([MOBILE_BASE_PATH+'work/<model("project.task.work"):work>/delete'],type='http', auth="user", website=True)
    def work_delete(self, work=None, search='', **post):
        return self.do_delete(obj=work, base_path=MOBILE_BASE_PATH+'%s' %work.task_id.id)

    @http.route([MOBILE_BASE_PATH+'<model("project.task"):task>/works/edit_grid'],type='http', auth="user", website=True)
    def work_edit_grid(self, task=None, search='', **post):
        if task:
            return self.do_grid(obj_ids=task.work_ids)
