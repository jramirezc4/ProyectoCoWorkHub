from django.urls import path

from .views import CreateReservationView

app_name = 'reservas'

urlpatterns = [
    path('crear/', CreateReservationView.as_view(), name='create'),
]