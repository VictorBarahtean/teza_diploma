from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views



urlpatterns = [
    #path('login/', views.user_login, name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/change_pass_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/change_pass_done.html'), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/reset_pass_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/reset_pass_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/reset_pass_confirm.html'), name='password_reset_confirm'),
    path('reset/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/reset_pass_complete.html'), name='password_reset_complete'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('user/', views.user_list, name='user_list'),
    path('user/followers/', views.followers_list, name='followers_list'),
    path('user/followed/', views.followed_list, name='followed_list'),
    path('user/search_user/', views.search_user, name='search_user'),
    path('user/follow/', views.user_follow, name='user_follow'),
    path('user/<username>/', views.user_detail, name='user_detail'),
]