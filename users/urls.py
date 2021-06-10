from django.urls import path

from users import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', views.LoginViewSet.as_view()),
]
