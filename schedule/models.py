import datetime

from django.db import models # Default

from django.urls import reverse # Used to generate URLs by reversing the URL patterns.
from django.contrib.auth.models import User # Used to assign 'Users' to models fields.
import uuid # Requred for Slot

# Event class.
# These are the events users create when they need subs.
# Subs than accept an open 'slot'
class Event(models.Model):
	title			= models.CharField(max_length=20) # The name the user assigns to the event.
	sport			= models.CharField(max_length=20) # Will eventually make this a drop down but need to learn how to specify 'other'.
	organizer		= models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	# date			= models.DateField()
	# time			= models.TimeField()
	datetime		= models.DateTimeField(auto_now=False, auto_now_add=False)
	location		= models.CharField(max_length=100)
	details			= models.TextField(max_length=1000, help_text="Enter some event details", null=True, blank=True)
	total_slots		= models.IntegerField()

	EVENT_STATUS	= (
		('o', 'Upcoming'),
		('f', 'Filled'),
		('c', 'Cancelled'),
		('d', 'Done')
	)

	status			= models.CharField(max_length=1, choices=EVENT_STATUS, default='o')

	def __str__(self):
		# String for representing the Model object.
		return f'{self.title}'

	def get_absolute_url(self):
		# Returns the url to access a detail record for this book.
		return reverse('event-detail', args=[str(self.id)])

	# Save override to create event 'slots' when the Event is created.
	# The number of Slot instances created is defined by the value in the 'total_slots' field.
	def save(self, *args, **kwargs):
		created = not self.pk
		super().save(*args, **kwargs)
		if created:
			for slot in range(self.total_slots):
				Slot.objects.create(event=self)

# Slot class
# These are the available positions for each event (i.e. how many subs are needed).
# Slots should be automatically created when an event is created.
# The number of slots created is defined by the 'total_slots' field in the Event class.
# The 'event' field should then be autofilled with the 'id' of the event that created the slot.
# The 'player' field is then filled in with the 'user' who accepted the slot.
class Slot(models.Model):
	id 		= models.UUIDField(primary_key=True, default=uuid.uuid4)
	event 	= models.ForeignKey('Event', on_delete=models.SET_NULL, null=True, blank=True)
	player 	= models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		# String for representing the Model object.
		return f'{self.id}'
