from django.urls import path
from . import views
app_name = 'SignIn'
urlpatterns = [
    path('',views.index,name='index'),
    path('signup/',views.SignUpPage,name='signuppage'),
    path('signup/done',views.SignUp,name='signup')
]