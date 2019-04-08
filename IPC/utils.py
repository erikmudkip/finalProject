from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import *

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None, course_id=None, user_type=None):
		"""calendar initialisation

	    .. note::This code was made by following this tutorial "https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html". Some part of the code is change in order to be able to be integrated to the webapp

	    :param self: object that contains metadata about the request.
	    :param year: object that contain the year.
	    :param month: object that contain the month.
		:param course_id: object that contain the ID of the course picked at course page.
		:param user_type: object that contain a string that have value of "student or "teacher".

	    :returns: initialize the calendar
	    """
		self.year = year
		self.month = month
		self.course_id = course_id
		self.user_type = user_type
		super(Calendar, self).__init__()

	def formatday(self, day, events):
		"""format day

	    .. note::This code was made by following this tutorial "https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html". Some part of the code is change in order to be able to be integrated to the webapp

	    :param self: object that contains metadata about the request.
	    :param day: object that contain the day.
	    :param events: object that contains the event on the day.

	    :returns: HTML code to create the calendar page.
	    """
		events_per_day = events.filter(eventDate__day=day)
		d = ''
		for event in events_per_day:
			d += f'<li> {event.get_html_url} </li>'

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr
	def formatweek(self, theweek, events):
		"""format week

	    .. note::This code was made by following this tutorial "https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html". Some part of the code is change in order to be able to be integrated to the webapp

	    :param self: object that contains metadata about the request.
	    :param theweek: object that contain the week.
	    :param events: object that contains the event on the week.

	    :returns: HTML code to create the calendar page.
	    """
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		"""format month

	    .. note::This code was made by following this tutorial "https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html". Some part of the code is change in order to be able to be integrated to the webapp

	    :param self: object that contains metadata about the request.
	    :param withyear: object that contain a boolean.

	    :returns: cal (return the calendar object.).
	    """
		events = Event.objects.filter(eventDate__year=self.year, eventDate__month=self.month, eventCourse=self.course_id)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal
