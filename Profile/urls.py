from django.urls import path 
from . import views

urlpatterns=[
	path('get-profile/', views.get_profile),
	path('update/', views.update_profile),
	path('search/<str:username>/', views.search),
	path('view-profile/<int:pk>/', views.view_profile),
	path('view_my_followers/', views.view_my_followers),
	path('view_following/', views.view_following),
	path('make_private/', views.make_private),
	path('unmake_private/', views.unmake_private),
	path('follow/<str:username>/', views.follow),
	path('unfollow/<str:username>/', views.unfollow),
	path('get_pending_list/', views.get_pending_list),
	path('approve/<int:pk>/', views.approve),
	path('disapprove/<int:pk>/', views.disapprove),
	path('block_user/<str:username>/', views.block_user),
	path('unblock<str:username>/', views.unblock),
	path('get_block_list/', views.get_block_list),
	path('get_follow_suggestions/', views.get_follow_suggestions),
]