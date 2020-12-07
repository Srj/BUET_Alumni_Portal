from django.urls import path
from . import views
app_name = 'community'

urlpatterns = [
    path('home/<int:my_groups_start>/<int:other_groups_start>/<int:comm_search_change>/<int:post_start>/<int:post_change>', views.home, name='home'),
    path('create_community', views.create_community, name="create_community"),
    path('create_comm_upload', views.create_comm_upload, name="create_comm_upload"),
    path("detail_community/<int:community_id>/<int:start_member_count>/<int:start_requ_count>/<int:post_start>/<int:post_change>", views.detail_community, name="detail_community"),
    path("join_request/<int:community_id>", views.join_request, name="join_request"),
    path("cancel_join_request/<int:community_id>", views.cancel_join_request, name="cancel_join_request"),
    path("join_community/<int:community_id>/<int:user_id>/<int:start_member_count>/<int:start_requ_count>", views.join_community, name="join_community"),
    path("remove_request/<int:community_id>/<int:user_id>/<int:start_member_count>/<int:start_requ_count>", views.remove_request, name="remove_request"),
    path("make_post/<int:community_id>", views.make_post, name="make_post"),
    path("upload_post/<int:community_id>", views.upload_post, name="upload_post"),
    path("detail_post/<int:community_id>/<int:post_id>/<int:start_from>", views.detail_post, name="detail_post"),
    path("upload_comment/<int:community_id>/<int:post_id>", views.upload_comment, name="upload_comment"),
    path("delete_group/<int:community_id>", views.delete_group, name="delete_group"),
    path("leave_group/<int:community_id>", views.leave_group, name="leave_group"),
    path("delete_post/<int:community_id>/<int:post_id>/<int:member_start>/<int:requ_start>", views.delete_post, name="delete_post"),
    path("delete_comment/<int:community_id>/<int:post_id>/<int:comment_id>", views.delete_comment, name="delete_comment")
    
]