from django.urls import path 
from . import views

urlpatterns = [ 
    path('', views.home, name='home'),
    path('offers/', views.offers, name='offers'),
    path('create-offer/', views.create_offer, name='create-offer'),
    path('view-offer/<slug:slug>', views.view_offer, name='view-offer'),
    path('delete-offer/<slug:slug>', views.delete_offer, name='delete-offer'),
    path('edit-offer/<slug:slug>', views.edit_offer, name='edit-offer'),
    path('enquire/<slug:slug>', views.enquire, name='enquire'),
]