
from django.urls import path
from. import views
from . views import *
urlpatterns = [
    path('admin_data/', AdminAPI.as_view()),           # GET all admins, POST new admin
    path('admin_data/<int:pk>/', AdminAPI.as_view()), # GET single, PUT, PATCH, DELETE
    path('login/', AdminLoginAPIView.as_view()),
    path('admin/profile/', AdminVerifyTokenAPIView.as_view()),
    path("category/", CategoryAPI.as_view()),
    path("category/<int:id>/", CategoryAPI.as_view()),
    path("influencers/", InfluencerAPI.as_view()),
    path("influencers/<int:id>/", InfluencerAPI.as_view()),
    path('banners/', BannerAPIView.as_view(), name='banner-list'),       # GET all, POST new
    path('banners/<int:pk>/', BannerAPIView.as_view(), name='banner-detail'),
    path('sponsored_content/', SponsoredContentAPIView.as_view()),
    path('sponsored_content/<int:pk>/', SponsoredContentAPIView.as_view()),
]