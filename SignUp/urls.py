from django.urls import path
from . import views
app_name = 'SignUp'
urlpatterns = [
    path('signup/',views.SignUp,name='signup'),
]