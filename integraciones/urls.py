from django.urls import path

from .views import available_spaces


urlpatterns = [
    path('', available_spaces, name='available-spaces'),
]
