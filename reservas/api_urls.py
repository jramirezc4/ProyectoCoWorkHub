from django.urls import path

from reservas.api_views import ReservationCollectionAPIView, ReservationDetailAPIView

app_name = 'reservas_api'

urlpatterns = [
    path('', ReservationCollectionAPIView.as_view(), name='reservation-collection'),
    path('<int:pk>/', ReservationDetailAPIView.as_view(), name='reservation-detail'),
]