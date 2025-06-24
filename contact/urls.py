from django.urls import path
from .views import SavedContactsListView, AddRemoveSavedContactView, RecentlyViewedContactsListView

urlpatterns = [
    path('saved/', SavedContactsListView.as_view(), name='saved-contacts-list'),
    path('create-update/', AddRemoveSavedContactView.as_view(), name='toggle-saved-contact'),
    path('recently-viewed/', RecentlyViewedContactsListView.as_view(), name='recently-viewed-list'),
]
