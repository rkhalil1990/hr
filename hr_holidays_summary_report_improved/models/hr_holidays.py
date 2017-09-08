# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _

import time
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import math
import pytz

import logging
_logger = logging.getLogger(__name__)
    
    
class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    date_day_from = fields.Date(string="Date From")
    date_day_to = fields.Date(string="Date To")

    day_time_from = fields.Selection([('morning', 'Morning'), ('midday', 'Midday')], string="Day Time From", default='morning')
    day_time_to = fields.Selection([('midday', 'Midday'), ('evening', 'Evening')], string="Day Time From", default='evening')

    @api.model
    def float_time_convert(self, float_val):    
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        hour = factor * int(math.floor(val))
        minute = int(round((val % 1) * 60))
        return format(hour, '02') + ':' + format(minute, '02')

    @api.one
    @api.onchange('date_day_from', 'day_time_from')
    def onchange_date_from(self):

        if not self.date_day_from or not day_time_from:
            return

        calendar_ids = self.env['resource.calendar'].search([('company_id', '=', self.employee_id.company_id.id)])

        morning = 8
        midday = 13

        date = datetime.strptime(self.date_day_from, DEFAULT_SERVER_DATE_FORMAT)

        if len(calendar_ids) > 0:
            for attendance in calendar_ids[0].attendance_ids:
                if int(attendance.dayofweek) == date.weekday():
                    morning = attendance.hour_from
                    midday = (attendance.hour_to + attendance.hour_from) / 2
                    break

        date_str_local = self.date_day_from + ' ' + self.float_time_convert(midday if self.day_time_from=='midday' else morning) + ':00'

        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        date_str_utc = timezone.localize(datetime.strptime(date_str_local, '%Y-%m-%d %H:%M:%S')).astimezone(pytz.UTC)

        self.update({
            'date_from': date_str_utc
        })

    @api.one
    @api.onchange('date_day_to', 'day_time_to')
    def onchange_date_to(self):

        if not self.date_day_to or not day_time_to:
            return

        calendar_ids = self.env['resource.calendar'].search([('company_id', '=', self.employee_id.company_id.id)])

        evening = 18
        midday = 13

        date = datetime.strptime(self.date_day_to, DEFAULT_SERVER_DATE_FORMAT)

        if len(calendar_ids) > 0:
            for attendance in calendar_ids[0].attendance_ids:
                if int(attendance.dayofweek) == date.weekday():
                    evening = attendance.hour_to
                    midday = (attendance.hour_to + attendance.hour_from) / 2
                    break

        date_str_local = self.date_day_to + ' ' + self.float_time_convert(midday if self.day_time_to=='midday' else evening) + ':00'

        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        date_str_utc = timezone.localize(datetime.strptime(date_str_local, '%Y-%m-%d %H:%M:%S')).astimezone(pytz.UTC)

        self.update({
            'date_to': date_str_utc
        })