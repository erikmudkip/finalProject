from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import *

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None, course_id=None, user_type=None):
		self.year = year
		self.month = month
		self.course_id = course_id
		self.user_type = user_type
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(eventDate__day=day)
		d = ''
		if self.user_type == "teacher":
			for event in events_per_day:
				d += f'<li> {event.get_html_url} </li>'
		elif self.user_type == "student":
			for event in events_per_day:
				d += f'<li> {event.eventTitle} </li>'

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr
	def formatweek(self, theweek, events):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		events = Event.objects.filter(eventDate__year=self.year, eventDate__month=self.month, eventCourse=self.course_id)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal
