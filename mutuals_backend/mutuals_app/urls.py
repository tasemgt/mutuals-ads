from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('interests/', views.interests_handler),
    path('users/', views.users_handler),
    path('users/<int:pk>/', views.user_detail_handler),
    path('groups/', views.groups_handler, name='group-list-create'),
    path('subgroups/', views.subgroups_handler, name='subgroup-list-create'),
    path('login/', views.login, name='fake-login'),
    path('user-detail/<str:user_id>/', views.get_user_by_user_id, name='get-user-by-user-id'),


]   