from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name="main"),
    path('search/', views.search_view, name="search"),
    path('dashboard/<int:app_id>/', views.dashboard_view, name="dashboard"),
    path('tags', views.tags_view, name="tags"),
]
