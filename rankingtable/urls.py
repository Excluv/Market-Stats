from django.urls import path

from . import views


urlpatterns = [
    path('', views.Index.as_view()),
    path('assetclass=<assetclass>/', views.AssetClass.as_view()),
]
