from django.urls import path
from .views import (
    AdminDefiListView, AdminDefiDetailView,
    AdminDefiCreateView, AdminDefiUpdateView, AdminDefiDeleteView,
    AdminObjectiveListView, AdminObjectiveCreateView, AdminObjectiveUpdateView, AdminObjectiveDeleteView,
    AdminBadgeListView, AdminBadgeCreateView, AdminBadgeUpdateView, AdminBadgeDeleteView,
    AdminStatusListView, AdminStatusCreateView, AdminStatusUpdateView, AdminStatusDeleteView,
    AdminNumberListView, AdminNumberCreateView, AdminNumberUpdateView, AdminNumberDeleteView,
    AdminRangeListView, AdminRangeCreateView, AdminRangeUpdateView, AdminRangeDeleteView,
)

app_name = 'defis_admin'

urlpatterns = [
    # Defi CRUD
    path('', AdminDefiListView.as_view(), name='list'),
    path('create/', AdminDefiCreateView.as_view(), name='create'),
    path('<int:pk>/', AdminDefiDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', AdminDefiUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', AdminDefiDeleteView.as_view(), name='delete'),



    # Objectives
    path('objectives/', AdminObjectiveListView.as_view(), name='objectives_list'),
    path('objectives/create/', AdminObjectiveCreateView.as_view(), name='objectives_create'),
    path('objectives/<int:pk>/edit/', AdminObjectiveUpdateView.as_view(), name='objectives_edit'),
    path('objectives/<int:pk>/delete/', AdminObjectiveDeleteView.as_view(), name='objectives_delete'),

    # Badges
    path('badges/', AdminBadgeListView.as_view(), name='badges_list'),
    path('badges/create/', AdminBadgeCreateView.as_view(), name='badges_create'),
    path('badges/<int:pk>/edit/', AdminBadgeUpdateView.as_view(), name='badges_edit'),
    path('badges/<int:pk>/delete/', AdminBadgeDeleteView.as_view(), name='badges_delete'),

    # Status
    path('status/', AdminStatusListView.as_view(), name='status_list'),
    path('status/create/', AdminStatusCreateView.as_view(), name='status_create'),
    path('status/<int:pk>/edit/', AdminStatusUpdateView.as_view(), name='status_edit'),
    path('status/<int:pk>/delete/', AdminStatusDeleteView.as_view(), name='status_delete'),

    # Numbers
    path('numbers/', AdminNumberListView.as_view(), name='numbers_list'),
    path('numbers/create/', AdminNumberCreateView.as_view(), name='numbers_create'),
    path('numbers/<int:pk>/edit/', AdminNumberUpdateView.as_view(), name='numbers_edit'),
    path('numbers/<int:pk>/delete/', AdminNumberDeleteView.as_view(), name='numbers_delete'),

    # Ranges
    path('ranges/', AdminRangeListView.as_view(), name='ranges_list'),
    path('ranges/create/', AdminRangeCreateView.as_view(), name='ranges_create'),
    path('ranges/<int:pk>/edit/', AdminRangeUpdateView.as_view(), name='ranges_edit'),
    path('ranges/<int:pk>/delete/', AdminRangeDeleteView.as_view(), name='ranges_delete'),
]
