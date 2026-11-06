from django.urls import path

from .views import CreateReviewView, EditReviewView

urlpatterns = [
    path('crear/<int:reservation_id>/', CreateReviewView.as_view(), name='review-create'),
    path('editar/<int:reservation_id>/', EditReviewView.as_view(), name='review-edit'),
]
