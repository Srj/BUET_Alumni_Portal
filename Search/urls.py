from django.urls import path
from . import views
app_name = 'Search'
urlpatterns = [
    path('',views.search,name='search'),
]