from django.urls import include, path

urlpatterns = [path('__vb_baseapp__/', include('vb_baseapp.urls', namespace='vb_baseapp'))]
