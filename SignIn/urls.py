from django.urls import path
from . import views
app_name = 'SignIn'
urlpatterns = [
    path('',views.SignIn,name='signin'),
]