from django.urls import path
from addon import views

app_name = 'addon'

urlpatterns = [
    path('aboutme/', views.about_me, name='aboutme'),
]