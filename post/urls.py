from django.urls import path
from . import views
app_name = 'post'

urlpatterns = [
    path('all_post/<int:start_from>/<int:change>', views.all_post, name='all_post'),
    path('make_post', views.make_post, name='make_post'),
    path('detail_post/<int:post_id>/<int:start_from>', views.detail_post, name='detail_post'),
    path('upload_post', views.upload_post, name='upload_post'),
    path('upload_comment/<int:post_id>', views.upload_comment, name='upload_comment'),
    path("delete_post/<int:post_id>", views.delete_post, name="delete_post"),
    path("delete_comment/<int:post_id>/<int:comment_id>", views.delete_comment, name="delete_comment")
]