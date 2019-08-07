from django.urls import path

from lecture_room_service import views

urlpatterns = [
    # API Version 1
    path('lecture/', views.ApiLectures.as_view(), name='lectures'),
    path('room/', views.ApiRooms.as_view(), name='rooms'),
    path('staircase/', views.ApiRoomCoord.as_view(), name='staircase-room'),
]
