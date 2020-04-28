import datetime	# In order to check input date vs current day's date.
from django.utils import timezone
import pytz

from django import forms

# For user sign up.
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput, DateTimePickerInput

from django.core.exceptions import ValidationError # To verify date.
from django.utils.translation import ugettext_lazy as _ 
from django.utils.safestring import mark_safe

from .models import Event

# Event Create form
class EventCreateForm(forms.ModelForm):
	class Meta:
		model = Event
		exclude = ['organizer', 'status']

	title		= forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'textinput textInput form-control'}))
	sport		= forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'textinput textInput form-control'}))
	datetime 	= forms.DateTimeField(widget=DateTimePickerInput(format='%m/%d/%Y %I:%M %p', attrs={'class': 'textinput textInput form-control'}))
	location	= forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'textinput textInput form-control', 'placeholder': '555 Fake St, Town, State Zip'}))
	details		= forms.CharField(max_length=100, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5', 'placeholder': 'Add any extra details you think are necessary (e.g. Park across the street. Wear a red shirt. etc.).'}))
	total_slots	= forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'numberinput form-control'}))

	# Prevent a date before the current date from being selected for 'date' field.
	def clean_datetime(self):
		input_datetime = self.cleaned_data['datetime']

		# Check if input date is before today.
		if input_datetime < datetime.datetime.now(tz=pytz.UTC):
			raise ValidationError('Invalid date and time. Cannot select a date and time in the past.')

		return input_datetime



# Event Update form
class EventUpdateForm(forms.ModelForm):
	class Meta:
		model = Event
		exclude = ['organizer', 'total_slots', 'status']

	title		= forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'textinput textInput form-control'}))
	sport		= forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'textinput textInput form-control'}))
	datetime 	= forms.DateTimeField(widget=DateTimePickerInput(format='%m/%d/%Y %I:%M %p', attrs={'class': 'textinput textInput form-control'}))
	location	= forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'textinput textInput form-control', 'placeholder': '555 Fake St, Town, State Zip'}))
	details		= forms.CharField(max_length=100, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}))

		# Prevent a date before the current date from being selected for 'date' field.
	def clean_datetime(self):
		input_datetime = self.cleaned_data['datetime']

		# Check if input date is before today.
		if input_datetime < datetime.datetime.now(tz=pytz.UTC):
			raise ValidationError('Invalid date. Cannot select a date in the past.')

		return input_datetime


# User Sign Up Form
class SignUpForm(UserCreationForm):
	username = forms.RegexField(
	    label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
	    help_text=("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
	    error_messages={
	        'invalid': _("This value may contain only letters, numbers and "
	                     "@/./+/-/_ characters.")},
	    widget=forms.TextInput(attrs={'class': 'textinput textInput form-control',
	                            'required': 'true'
	    })
	)

	first_name = forms.CharField(
		max_length=30, 
		help_text='Required. Please enter your First Name.',
		widget=forms.TextInput(attrs={'class': 'textinput textInput form-control',
										'required': 'true'}))
	last_name = forms.CharField(
		max_length=30,
		help_text='Required. Please enter your First Name.',
		widget=forms.TextInput(attrs={'class': 'textinput textInput form-control',
										'required': 'true'}))
	# email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
	email = forms.CharField(
	    label=_("Email"),
	    help_text='Required. Inform a valid email address.',
	    widget=forms.TextInput(attrs={'class': 'form-control',
	                                	'type': 'email',
	                                	'required': 'true'

	    })
	)

	password1 = forms.CharField(
	    label=_("Password"),
	    help_text=mark_safe('Your password can’t be too similar to your other personal information.<br />'
	    			'Your password must contain at least 8 characters.<br />'
					'Your password can’t be a commonly used password.<br />'
					'Your password can’t be entirely numeric.'),
	    widget=forms.PasswordInput(attrs={'class': 'form-control',
	    									'type': 'password',
	                                    	'required': 'true',

	    })
	)

	password2 = forms.CharField(
	    label=_("Password confirmation"),
	    widget=forms.PasswordInput(attrs={'class': 'form-control',
	                                      'type': 'password',
	                                      'required': 'true',
	    }),
	    help_text=_("Enter the same password as above, for verification.")
	)

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')







