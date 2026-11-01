from django.urls import path

from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.home, name='home'),
    path('poll/<int:poll_id>/', views.vote, name='vote'),
    path('poll/<int:poll_id>/results/', views.results, name='results'),
    path('poll/<int:poll_id>/results.json', views.results_json, name='results_json'),
]
