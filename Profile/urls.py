from django.urls import path 
from . import views

urlpatterns=[
	path('get-profile/', views.get_profile),
	path('update/', views.update_profile),
	path('search/<str:username>/', views.search),
	path('view-profile/<int:pk>/', views.view_profile),
	path('view_my_followers/', views.view_my_followers),
	path('view_following/', views.view_following),
]