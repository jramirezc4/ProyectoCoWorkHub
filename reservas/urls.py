from django.urls import path

from .views import CancelReservationView, CreateReservationView

app_name = 'reservas'

urlpatterns = [
    path('crear/', CreateReservationView.as_view(), name='create'),
    path('<int:pk>/cancelar/', CancelReservationView.as_view(), name='cancel'),
]