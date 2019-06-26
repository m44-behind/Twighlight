"""crud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from boards import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('streamer/', views.streamer, name='streamer'),
    path('streamer/<int:streamer_sid>/video/', views.video, name='video'),
    path('streamer/<int:streamer_sid>/video/<int:video_vid>/chat/', views.chat,  name='chat')
    # path 를 타고 나가면 views.chat의 내요을 뿌리겠다 ?
]
