from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Cooks
    path('cooks/', views.cook_list, name='cook_list'),
    path('cooks/<int:cook_id>/', views.cook_profile, name='cook_profile'),

    # Booking
    path('book/<int:cook_id>/', views.book_cook, name='book_cook'),
    path('bookings/<int:booking_id>/confirm/', views.confirm_booking, name='confirm_booking'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/<int:booking_id>/pay/', views.pay_booking, name='pay_booking'),
    path('bookings/<int:booking_id>/complete/', views.complete_booking, name='complete_booking'),

    # Dashboards
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/cook/', views.cook_dashboard, name='cook_dashboard'),

    # Reviews
    path('cooks/<int:cook_id>/review/', views.add_review, name='add_review'),

    # Profile
    path('profile/', views.profile, name='profile'),
]

