from django.urls import path
from . import views
app_name = 'Profile'
urlpatterns = [
    path('',views.index,name='profile'),
    path('edit',views.edit,name='edit_profile'),
    path('search',views.search,name='search'),
    path('edit_photo',views.edit_photo,name='edit_photo'),
    path('edit_expertise',views.edit_expertise,name='edit_expertise'),
    path('delete_expertise',views.delete_expertise,name='delete_expertise'),
    path('edit_job',views.edit_job,name='edit_job'),
    path('delete_job',views.delete_job,name='delete_job'),
    path('<int:std_id>/',views.visit_profile,name='visit_profile'),
    path('<int:std_id>/endorse/<str:topic>/',views.endorse,name='endorse'),
]