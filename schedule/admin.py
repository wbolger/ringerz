from django.contrib import admin

from .models import Event, Slot # Bring in the created models Event and Slot

admin.site.register(Event)

# Improve the list display for slots to show the Event they belong to as well on the admin page.
@admin.register(Slot)
class EventAdmin(admin.ModelAdmin):
	list_display = ('id', 'event')