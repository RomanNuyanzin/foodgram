from django.urls import include, path

urlpatterns = [
    path('', include('recipes.urls')),
    path('', include('users.urls')),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]