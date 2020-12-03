from django.urls import path
from . import views
app_name = 'community'

urlpatterns = [
    path('home/<int:my_groups_start>/<int:other_groups_start>/<int:comm_search_change>', views.home, name='home'),
    path('create_community', views.create_community, name="create_community"),
    path('create_comm_upload', views.create_comm_upload, name="create_comm_upload"),
    path("detail_community/<int:community_id>/<int:start_member_count>/<int:start_requ_count>", views.detail_community, name="detail_community"),
    path("join_request/<int:community_id>", views.join_request, name="join_request"),
    path("join_community/<int:community_id>/<int:user_id>/<int:start_member_count>/<int:start_requ_count>", views.join_community, name="join_community"),
    path("remove_request/<int:community_id>/<int:user_id>/<int:start_member_count>/<int:start_requ_count>", views.remove_request, name="remove_request"),
    
]