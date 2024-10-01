from django.urls import path
from . import views

urlpatterns = [
	path('get_notifications/', views.get_notifications),
	path('mark_as_read/<int:pk>/', views.mark_as_read),
	path('get_comment_notifications/', views.get_comment_notifications),
	path('mark_comment_notif_as_read/<int:pk>/', views.mark_comment_as_read),
]