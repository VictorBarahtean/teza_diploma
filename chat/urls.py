from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.messages_page, name='messages_page'),
    path('createth/<username>/', views.create_thread, name='create_thread'),
    path('detail_usr/', views.detail_usr, name='detail_usr'),
]