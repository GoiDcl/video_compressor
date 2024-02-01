from django.contrib import admin
from django.urls import include, path
# from drf_yasg import openapi
# from drf_yasg.views import get_schema_view
from rest_framework import routers
from rest_framework.authtoken import views

from .views import VideoCompressorViewSet

router = routers.SimpleRouter()

router.register(r'compressor', VideoCompressorViewSet, basename='comressor')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', views.obtain_auth_token),
    path('', include(router.urls)),
]

# schema_view = get_schema_view(
#    openapi.Info(
#        title="overflow",
#        default_version='v1',
#        description="Документация для приложения фиксации переполнения"
#                    "/автоочистки устройств",
#    ),
#    public=True,
#    permission_classes=(permissions.AllowAny,),
# )
#
# urlpatterns += [
#     re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None),
#             name='schema-redoc'),
# ]
