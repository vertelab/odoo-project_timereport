# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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

from openerp import models, fields, api, _
import openerp.tools
#import re
#import time
#from datetime import date, datetime, timedelta
#from dateutil.relativedelta import relativedelta

class todo_list(models.Model):
    _name = 'project.timereport.todo'
    _description = 'Todo List'
    
    activity = fields.Text(string = 'Activity Description', required=False)
    state = fields.Selection([('none','None'),('start','Start'),('stop','Stop')], string='Activity State', required=True, default = 'none')
