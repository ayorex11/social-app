from django.urls import path
from . import views

urlpatterns = [
	path('create_post/', views.create_post),
	path('comment/', views.comment),
	path('like_post/<int:pk>/', views.like_post),
	path('get_post_likes/<int:pk>/', views.get_post_likes),
	path('like_comment/<int:pk>/', views.like_comment),
	path('get_comment_likes/<int:pk>/', views.get_comment_likes),
	path('unlike_post/<int:pk>/', views.unlike_post),
	path('unlike_comment/<int:pk>/', views.unlike_comment),
	path('delete_post/<int:pk>/', views.delete_post),
	path('delete_comment/<int:pk>/', views.delete_comment),
	path('get_post/<int:pk>/', views.get_post),
	path('get_my_posts/', views.get_my_posts),
	path('get_user_post/<str:username>/', views.get_user_post),
	path('timeline/', views.timeline),
]