from django.urls import path

from lector import views

urlpatterns = [
    # API Version 1
    path('movement-types/', views.ApiListMovementTypes.as_view(), name='movement-types'),
    path('open-space/', views.ApiListOpenSpaces.as_view(), name='open-spaces'),
    path('open-space/plot/', views.ApiOpenSpaceInfos.as_view(), name='open-spaces-plot'),
]
