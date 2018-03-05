from .views import UserViewSet, UserProfileViewSet, RelationShipViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'users', UserViewSet, base_name='user')
router.register(r'profiles', UserProfileViewSet, base_name='profile')
router.register(r'relationships', RelationShipViewSet, base_name='relationship')

urlpatterns = router.urls