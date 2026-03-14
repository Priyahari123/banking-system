from django.urls import path
from .views import *


urlpatterns = [
    path('api/account/apply_interest/', ApplyInterestAPIView.as_view(), name='apply-interest'),
    path('api/login/', LoginAPIView.as_view()),
    path('api/account/<str:customer_id>/', AccountDetailAPIView.as_view()),
    path('api/loan/pay/', PayLoanAPIView.as_view()),
    path('api/user/create/', CreateUserAPIView.as_view()),
    path('api/loan/create/', CreateLoanAPIView.as_view())
]