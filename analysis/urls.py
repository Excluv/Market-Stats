from django.urls import path

from . import views


urlpatterns = [
    path("product=<product>/sector=<sector>/", views.ChartData.as_view()),
    path("product=<product>/sector=<sector>/period=<startdate>-<enddate>/metric=<metric>", views.TableData.as_view()),
]
