"""SJTB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from tools import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tools/', views.toolsIndex),
    path('tools/e-book', views.downloadBookView),
    path('tools/e-book/search', views.searchBookAction),
    path('tools/e-book/download',views.downloadBookNew),
    path('tools/audio/transform',views.audioTransformView),
    path('tools/audio/transform_action',views.audioTransformAction)
]
