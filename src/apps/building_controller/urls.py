from django.urls import path

from . import views

urlpatterns = [
    # API Version 1
    path('buildings/', views.ApiBuildings.as_view(), name='buildings'),
    path('buildings/<str:file_name>/', views.ApiBuilding.as_view(), name='building'),
    path('buildings/<str:building_key>/<str:level>/<str:number>/', views.ApiRoomBuilding.as_view(),
         name='room-building'),
    path('buildings/<str:building_key>/staircases/<str:level>/<str:number>/coord/', views.ApiRoomCoord.as_view(), name='staircase-room'),
]
