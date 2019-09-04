from django.urls import path

from apps.univis_controller import views

urlpatterns = [
    # API Version 1
    path('univis/lectures/', views.ApiLectures.as_view(), name='lectures'),
    path('univis/rooms/', views.ApiRooms.as_view(), name='rooms'),
]
