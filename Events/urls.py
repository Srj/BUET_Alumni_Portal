from django.urls import path
from . import views
app_name = 'Events'
urlpatterns = [
    path('',views.index,name='events'),
    path('<int:event_id>/',views.visit_event,name='visit_event'),
    path('create/',views.make_event,name='make_event'),
]