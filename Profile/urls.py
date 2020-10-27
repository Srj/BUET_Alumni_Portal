from django.urls import path
from . import views
app_name = 'Profile'
urlpatterns = [
    path('',views.index,name='profile'),
    path('/edit',views.edit,name='edit_profile'),
]