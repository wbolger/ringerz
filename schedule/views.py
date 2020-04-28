import datetime
from django.utils import timezone
import pytz

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .models import Event, Slot # Import models
from django.views import generic # Import the generic views to build the custom views from.
from django.views.generic.edit import CreateView, UpdateView # Specific import for creating and editting an event.
from django.contrib.auth.models import User # To get user information.
from django.db.models import Q # For search

from .forms import SignUpForm, EventCreateForm, EventUpdateForm # Import custom forms.

# Needed to check if users are authenticated in order to create new events and accept slots.
from django.contrib.auth.mixins import LoginRequiredMixin

# For new user sign up
from django.contrib.auth import login, authenticate

# List of Events (also the Home view when the user goes to '/')
class EventListView(generic.ListView):
	model = Event

	# Queryset is used for 'search'.
	# If there is no query variable, the whole list of 'open' events is returned.
	# If there is a query variable, the list is filtered through the 'title' and 'sport' fields.
	def get_queryset(self):
		query = self.request.GET.get('q')
		if query:
			return Event.objects.filter(Q(title__icontains=query) | Q(sport__icontains=query))
		else:
			return Event.objects.filter(Q(status='o') | Q(status='f'))

# Event details view so users can see all of the event details
class EventDetailView(generic.DetailView):
	model = Event

# Create a new event.
class NewEventCreateView(LoginRequiredMixin, CreateView):
	model = Event
	# fields = ['title', 'sport', 'date', 'time', 'location', 'details', 'total_slots']
	form_class = EventCreateForm

	# 'form_valid' override to save current user to the Event 'organizer' field on form submission.
	def form_valid(self, form):
		form.instance.organizer = self.request.user
		return super().form_valid(form)

# Edit an event.
# Simple form to edit an event.
# Form, however, cannot be used to update slot number.
# Separate view is required to update slots.
# View also prevents anyone other than they event 'organizer' from editting the event.
@login_required
def EventUpdateView(request, pk):
	event = get_object_or_404(Event, pk=pk)

	if request.user == event.organizer:
		if request.method == 'POST':
			form = EventUpdateForm(request.POST, instance=event)
			if form.is_valid():
				form.save()
				return redirect(event.get_absolute_url())
		if request.method == 'GET':
			form = EventUpdateForm(instance=event)
		context = {
			'form': form,
			'event': event
		}
		return render(request, 'schedule/event_update_form.html', context)
	else:
		return render(request, 'schedule/blocks/event_update_block.html', {})

# Update the Status of an Event (cancel or re-open)
# When the view is loaded, depending on the event status (i.e. event.status) the user is prompted to cancel or reopen the event
# On the post, the status is set to either 'c' or 'o' depending on the previous state.
# View also blocks anyone who is not the event organizer from changing the status.
@login_required
def EventStatusUpdateView(request, pk):
	event = get_object_or_404(Event, pk=pk)

	if request.user == event.organizer:
		if request.method == 'POST':
			if event.status == 'o':
				event.status = 'c'
			elif event.status =='c':
				event.status = 'o'
			event.save()
			return redirect('event-list')
		if request.method == 'GET':
			return (render(request, 'schedule/event_status_update.html', {'event': event}))
	else:
		return (render(request, 'schedule/blocks/event_cancel_block.html', {}))


# View for player to confirm they want to join that event by accepting the Slot.
# Once the player confirms the acceptance, the Slot 'player' field is populated by the logged in user.
# View also blocks event organizer from joining one of the slots.
# View also blocks someone who has reserved a slot from taking another one.
@login_required
def SlotJoinView(request, pk):
	slot = get_object_or_404(Slot, pk=pk)
	queryset = Slot.objects.filter(event=slot.event)
	
	# Verify the slot status is 'open'. You cannot join as slot for an event that is 'filled', 'cancelled' or 'done'.
	if slot.event.status == 'o':

		# Verify slot is not taken (i.e slot.player has a value and is not null).
		# If the slot is occupied, the 'join' is blocked.
		if slot.player != None:
			return render(request, 'schedule/blocks/slot_join_block.html', {})

		# If slot.player is available (i.e. slot.player == None), check to make sure the user is not the event organizer.
		# If the user is the event organizer, the 'join' is blocked.
		if request.user == slot.event.organizer:
			return render(request, 'schedule/blocks/slot_join_block.html', {})

		# Go through each Slot associated to the event and check the assigned player.
		# If the current user appears in any other slot, then the loop exits and the 'join' is blocked.
		for query in queryset:
			if query.player != None:
				if query.player == request.user:
					return render(request, 'schedule/blocks/slot_join_block.html', {})

		# Once block checks have been made, the POST or GET is processed.
		# POST - current user is assigned to the slot instance. User is redirected to event details page.
		# GET - 'confirm join' form is rendered and the current user can confirm they want to join the event (submit trigger the POST).
		if request.method == 'POST':
			slot.player = request.user
			slot.save()
			# Now check to see if all slots are filled. If so, event status becomes 'Filled'.
			if slot.event.status == 'o':
				for idx, query in enumerate(queryset):
					if query == slot:
						if (idx+1) % query.event.total_slots == 0:
							slot.event.status = 'f'
					if query.player == None:
						break
					else:
						if (idx+1) % query.event.total_slots == 0:
							slot.event.status = 'f'
				slot.event.save()
			return redirect(slot.event.get_absolute_url())
		if request.method=='GET':
			return (render(request, 'schedule/slot_join.html', {'slot':slot}))
	else:
		return render(request, 'schedule/blocks/slot_join_block.html', {})

# View for player to confirm they want to leave an event after they have joined.
# Once the player confirms they want to leave, the Slot 'player' field is set to none.
# View also blocks anyone other than the slot.player from removing the player.
@login_required
def SlotRemoveView(request, pk):
	slot = get_object_or_404(Slot, pk=pk)
	
	# Check if the current user is the player assigned to the slot.
	# If not, the 'remove' is blocked.
	if request.user == slot.player:
		if request.method == 'POST':
			slot.player = None
			slot.save()
			# Only reopened events that are filled.
			# If an event is 'cancelled' or 'done', leaving the event does not change the event status.
			if slot.event.status == 'f':
				slot.event.status = 'o'
				slot.event.save()
			return redirect('event-detail', pk=slot.event.id)
		if request.method =='GET':
			return (render(request, 'schedule/slot_remove.html', {'slot': slot}))
	else:
		return (render(request, 'schedule/blocks/slot_remove_block.html', {}))

# View My Events
# View for the user to see the events they are the 'organizer' for
# View also to see the events where the user occupies one of the 'slots' (i.e. slot.player == user)
@login_required
def MyEventsView(request):

	events = Event.objects.filter(organizer=request.user).order_by('datetime') # Get all the events the user is the 'organizer'.
	slots = Slot.objects.filter(player=request.user) # Get all the slots the user is the 'player'.

	context = {
		'events': events,
		'slots': slots
	}

	return render(request, "schedule/myevents.html", context)

# View to see all the slots for an event and add/remove slots.
# Hitting add slot is a post which creates another slot with the slot.event = the current event.
# The number of slots associated to that event are counted and the total_slots are updated to that count.
# Each existing slot has a link to another view to confirm their deletion.
# View also blocks anyone other than the event 'organizer' from adding/removing slots.
@login_required
def EventSlotsUpdateView(request, pk):
	event = get_object_or_404(Event, pk=pk)

	if request.user == event.organizer:
		context = {
			'event': event
		}
		if request.method == 'POST':
			Slot.objects.create(event=event)
			event.total_slots = Slot.objects.filter(event=event).count() # Count new amount of slots for that event and update total_slots to that number.
			if event.status == 'f':
				event.status = 'o'
			event.save()
			return (render(request,"schedule/edit_slots.html", context))
		if request.method == 'GET':
			return (render(request,"schedule/edit_slots.html", context))
	else:
		return (render(request, 'schedule/blocks/event_update_block.html', {}))

# View to delete a slot
# User hits confirm to delete the slot entry (slot instance is completely deleted).
# The number of slots associated to that event are counted and the total_slots are updated to that count.
# User is returned to EventSlotsUpdateView.
# View also blocks anyone other than the event 'organizer' from deleting the slot.
@login_required
def EventSlotDeleteView(request, pk):
	slot = get_object_or_404(Slot, pk=pk)
	event = slot.event
	queryset = Slot.objects.filter(event=slot.event)

	if queryset.count() == 1:
		return redirect('event-slots-update', pk=event.id)

	if request.user == slot.event.organizer:
		if request.method == 'POST':
			# Block 'delete' if there is only one slot.
			if queryset.count() == 1:
				return redirect('event-slots-update', pk=event.id)
				# return (render(request, 'schedule/blocks/event_update_block.html', {}))
			slot.delete()
			# Count remaining slots for that event and update total_slots to that number.
			event.total_slots = queryset.count() 
			# Check if removing the slot now made the event 'filled'. Only do this if the event is 'open'.
			if event.status == 'o':
				for idx, query in enumerate(queryset):
					print(query, ' - ', query.player)
					if query.player == None:
						break
					else:
						if (idx+1) % event.total_slots == 0:
							event.status = 'f'
			event.save()
			return redirect('event-slots-update', pk=event.id)
		if request.method == 'GET':
			return (render(request,"schedule/slot_delete.html", {'slot': slot }))
	else:
		return (render(request, 'schedule/blocks/event_update_block.html', {}))

# User Sign Up
def userSignUpView(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('event-list')
	else:
		form = SignUpForm()
	context = {
		'form': form
	}
	return render(request, 'signup.html', context=context)












