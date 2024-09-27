from django.urls import path
from . import views

urlpatterns = [
	path('get_notifications/', views.get_notifications),
	path('mark_as_read/<int:pk>/', views.mark_as_read),
]