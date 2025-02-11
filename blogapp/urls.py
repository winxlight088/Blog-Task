from django.urls import path,include
from .views import *
from rest_framework import routers


#ROUTER in django rest_framework are desdinged to work with viewsets, wihich providew actions like post,create, retrieve...
router = routers.SimpleRouter()

router.register(r'post', PostViewSet, basename = 'post' )
router.register(r'user_register', UserViewSet, basename = 'register')
router.register(r'post_type_list', CategoryViewSet, basename = 'category_create')
router.register(r'user_comment',CommentViewSet, basename= 'comments')
# router.register(r"comment_detail", CommentDetailViewSet, basename = 'comment_detail')

urlpatterns = router.urls+ [
    # path('user_register/', UserRegisterView.as_view, name = 'register')
    # path('create_post/', PostCreateView.as_view, name = 'post')
    path('user_login/', LoginAPIView.as_view(), name= 'login'),
    
    
]
