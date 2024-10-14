from django.urls import path 
from . import views 

urlpatterns = [
	path('send_message/<str:username>/', views.send_message),
	path('get_chats/', views.get_chats),
	path('open_chat/<int:pk>/', views.open_chat),

]
