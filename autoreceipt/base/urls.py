from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

# patterns
urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('cleanup/home', views.home, name='home'),
    path('send-emails/', views.send_emails, name='send_emails'),
    path('save-receipts/', views.download_receipt, name='save_receipts'),
    path('template/', views.template, name='template'),
    path('cleanup/', views.cleanup, name='cleanup')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
