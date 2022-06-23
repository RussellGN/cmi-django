from django.urls import path 
from . import views

urlpatterns = [ 
    path('', views.home, name='home'),
    path('account/<slug:slug>', views.account, name='account'),
    path('user-login/', views.user_login, name='user-login'),
    path('user-logout/', views.user_logout, name='user-logout'),
    path('user-signup/', views.user_signup, name='user-signup'),
    path('notifications/', views.user_notifications, name='notifications'),
    path('offers/', views.offers, name='offers'),
    path('create-offer/', views.create_offer, name='create-offer'),
    path('view-offer/<slug:slug>', views.view_offer, name='view-offer'),
    path('delete-offer/<slug:slug>', views.delete_offer, name='delete-offer'),
    path('edit-offer/<slug:slug>', views.edit_offer, name='edit-offer'),
    path('update-profile/', views.update_profile, name='update-profile'),
    path('user-settings/', views.user_settings, name='user-settings'),
    path('update-inbox-settings/', views.update_inbox_settings, name='update-inbox-settings'),
    path('change-password', views.change_password, name='change-password'),
    path('change-display-photo/', views.change_display_photo, name='change-display-photo'),
    path('enquire/<slug:slug>', views.enquire, name='enquire'),
]