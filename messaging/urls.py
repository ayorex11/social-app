from django.urls import path 
from . import views 

urlpatterns = [
	path('send_message/<str:username>/', views.send_message),

]
