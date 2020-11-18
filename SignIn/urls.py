from django.urls import path
from . import views
app_name = 'SignIn'
urlpatterns = [
    path('',views.index,name='signin'),
    path('logout',views.logout,name='logout'),
]