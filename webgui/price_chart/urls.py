from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chart', views.chart, name="chart"),
    path('data', views.data, name="data"),
    path('retrieve', views.retrieve_data_from_api, name="retrieve")
]
