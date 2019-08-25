from django.urls import path

from apps.univis_controller import views

urlpatterns = [
    # API Version 1
    path('lecture/', views.ApiLectures.as_view(), name='lectures'),
    path('room/', views.ApiRooms.as_view(), name='rooms'),
]
