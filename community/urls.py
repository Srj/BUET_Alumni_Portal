from django.urls import path
from . import views
app_name = 'community'

urlpatterns = [
    path('home/<int:my_groups_start>/<int:other_groups_start>/<int:comm_search_change>', views.home, name='home'),
    path('create_community', views.create_community, name="create_community"),
    path('create_comm_upload', views.create_comm_upload, name="create_comm_upload")
    
]