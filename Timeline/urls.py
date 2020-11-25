from django.urls import path
from . import views
app_name = 'Timeline'
urlpatterns = [
    path('',views.index,name='timeline'),
]