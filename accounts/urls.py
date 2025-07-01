from django.urls import path
from . import views

urlpatterns = [
    path('request-otp/', views.RequestPhoneOTP.as_view()),
    path('verify-otp/', views.VerifyPhoneOTP.as_view()),
    path('signup/', views.SignupRequest.as_view()),
    path('finalize-signup/', views.FinalizeSignup.as_view()), 
    path('profile/', views.ProfileView.as_view()),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('profile-public/<int:pk>/', views.ProfilePublicDetailView.as_view(), name='profile-public-detail'),
]
