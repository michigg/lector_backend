from django.urls import path

from . import views

urlpatterns = [
    # API Version 1
    path('buildings/', views.ApiBuildings.as_view(), name='buildings'),
    path('buildings/<str:file_name>/', views.ApiBuilding.as_view(), name='building'),
    path('staircases/<str:building>/<str:level>/<str:number>/', views.ApiRoomCoord.as_view(), name='staircase-room'),
    # path('open-space/plot/', views.ApiOpenSpaceInfos.as_view(), name='open-spaces-plot'),
]
