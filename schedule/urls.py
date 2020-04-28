from django.urls import path
from django.conf.urls import url
from . import views # Import custom views.

urlpatterns = [
    path('', views.EventListView.as_view(), name='event-list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('newevent/', views.NewEventCreateView.as_view(), name='event-create'),
    path('slot/<uuid:pk>/join/', views.SlotJoinView, name='slot-join'),
    path('slot/<uuid:pk>/leave/', views.SlotRemoveView, name='slot-remove'),
    path('slot/<uuid:pk>/delete/', views.EventSlotDeleteView, name='slot-delete'),
    path('event/<int:pk>/eventupdate/', views.EventUpdateView, name='event-update'),
    path('event/<int:pk>/statusupdate/', views.EventStatusUpdateView, name='event-status-update'),
    path('event/<int:pk>/slotsupdate/', views.EventSlotsUpdateView, name='event-slots-update'),
    path('myevents/', views.MyEventsView, name='my-events')
]