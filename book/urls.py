from django.urls import path, include

from . import views

urlpatterns = [
    path('', include([
        path('', views.BookView.as_view({
            'get': 'list',
        })),

        path('<int:pk>/', include([
            path('', views.BookView.as_view({
                'get': 'retrieve',

            })),
            path('loan', views.BookView.as_view({
                'put': 'loan',
                'delete': 'back'
            })),

        ])),
    ]))]
