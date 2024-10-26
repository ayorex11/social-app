from django.urls import path 
from . import views 

urlpatterns = [
	path('send_message/<str:username>/', views.send_message),
	path('get_chats/', views.get_chats),
	path('open_chat/<int:pk>/', views.open_chat),
	path('edit_message/<int:pk>/', views.edit_message),
	path('edit_read_receipts/', views.edit_read_receipts),
	path('mark_as_read/<int:pk>/', views.mark_as_read),

]
