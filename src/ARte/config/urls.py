from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
import debug_toolbar

urlpatterns = [
    path('', include('core.urls')),
    path('', include('core.routes')),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('docs/', include('docs.urls'), name='docs'),
]

urlpatterns += [
    path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] 
    
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)