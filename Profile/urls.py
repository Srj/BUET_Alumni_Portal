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
    path('<int:std_id>/',views.visit_profile,name='visit_profile'),
]