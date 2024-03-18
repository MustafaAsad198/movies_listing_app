from django.urls import include, path, re_path
from . import views
from rest_framework.routers import DefaultRouter


urlpatterns = [
    # path('register',register,name='register'),
    re_path(r"^register$", views.register),
    re_path(r"^movies$", views.movies),
    re_path(r"^collection$", views.collection),
    re_path(r"^login$", views.custom_login),
    re_path(r"^logout$", views.custom_logout),
    re_path(r"^collection/(?P<pk>[a-zA-Z0-9-]+)$", views.update_collection),
    re_path(r"^request-count$", views.get_count),
    re_path(r"^request-count/reset$", views.reset_count),
]
