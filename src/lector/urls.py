from django.urls import path

from lector import views

urlpatterns = [
    # API Version 1
    path('movement-types/', views.ApiListMovementTypes.as_view(), name='movement-types'),
]
