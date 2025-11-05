from django.urls import path
from .views import (
    StoreListCreateView,
    MyStoreView,
    AllStoresView,
    ViewStoreEvent,
    LikeStoreView,
    FollowStoreView,
    CommentStoreView,
    StoreDetailsView,
    FavoriteStoreView,
    FavoriteStoresListView,
    FavoriteStoresByUserView,
    NearbyStoresView,
)

urlpatterns = [
    path('CreateStore', StoreListCreateView.as_view(), name='stores-list-create'),
    path('my-store', MyStoreView.as_view(), name='stores-my-store'),
    path('all-stores', AllStoresView.as_view(), name='stores-all'),
    path('view', ViewStoreEvent.as_view(), name='stores-view'),
    path('like', LikeStoreView.as_view(), name='stores-like'),
    path('follow', FollowStoreView.as_view(), name='stores-follow'),
    path('comment', CommentStoreView.as_view(), name='stores-comment'),
    path('details/<uuid:store_id>', StoreDetailsView.as_view(), name='stores-details'),
    path('favorite', FavoriteStoreView.as_view(), name='stores-favorite'),
    path('favorites', FavoriteStoresListView.as_view(), name='stores-favorites'),
    path('favorites/<uuid:user_id>', FavoriteStoresByUserView.as_view(), name='stores-favorites-user'),
    path('nearby', NearbyStoresView.as_view(), name='stores-nearby'),
]