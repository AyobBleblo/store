from django.contrib import admin
from django.urls import path , include
import debug_toolbar

admin.site.site_header = "Ayoub Store Admin Panel"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("playgrounde/", include("playgrounde.urls")),
    path("store_/",include("store_.urls")),
    path("__debug__", include(debug_toolbar.urls))
]
