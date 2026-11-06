from django.urls import path

from reservas.api_views import (
    ReservationAvailabilityAPIView,
    ReservationCollectionAPIView,
    ReservationDetailAPIView,
)

app_name = 'reservas_api'

urlpatterns = [
    path('disponibilidad/', ReservationAvailabilityAPIView.as_view(), name='reservation-availability'),
    path('', ReservationCollectionAPIView.as_view(), name='reservation-collection'),
    path('<int:pk>/', ReservationDetailAPIView.as_view(), name='reservation-detail'),
]