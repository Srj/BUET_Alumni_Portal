"""Alumni_Portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('SignUp.urls'),name='SignUp'),
    path('', include('SignIn.urls'),name='SignIn'),
    path('profile/',include('Profile.urls'),name='Profile'),
    path('post/', include('post.urls'), name='post'),
    path('Timeline/', include('Timeline.urls'), name='Timeline'),
    path('Search/', include('Search.urls'), name='Search'),
    path('community/', include('community.urls'), name='community')

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

