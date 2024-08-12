from rest_framework import routers
from unicodedata import name
from api.views import *

router = routers.DefaultRouter()

router.register(r'user', UserViewSet, basename='user')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'task', TaskViewSet, basename='task')
urlpatterns = router.urls
