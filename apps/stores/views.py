from math import radians, sin, cos, atan2, sqrt
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Store, StoreComment
from .serializers import StoreSerializer, StoreCreateSerializer, StoreCommentSerializer


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


class StoreListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Store.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StoreCreateSerializer
        return StoreSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'store'):
            raise generics.ValidationError({'detail': 'Store already exists for this user'})
        store_name = serializer.validated_data.get('store_name') or user.store_name
        serializer.save(user=user, store_name=store_name)


class MyStoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        store = getattr(request.user, 'store', None)
        if not store:
            return Response({'message': 'Store not found'}, status=404)
        return Response(StoreSerializer(store).data)

    def put(self, request):
        user = request.user
        if 'user_id' in request.data and str(request.data['user_id']) != str(user.id):
            return Response({'message': 'Unauthorized: user_id does not match authenticated user'}, status=403)
        store = getattr(user, 'store', None)
        if not store:
            return Response({'message': 'Store not found for the provided user_id'}, status=404)
        serializer = StoreSerializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Store updated successfully', 'store': StoreSerializer(store).data})


class AllStoresView(generics.ListAPIView):
    queryset = Store.objects.all().order_by('-created_at')
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]


class ViewStoreEvent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        store_id = request.data.get('store_id')
        if not store_id:
            return Response({'errors': [{'msg': 'Store ID is required'}]}, status=400)
        store = get_object_or_404(Store, id=store_id)
        Store.objects.filter(id=store.id).update(views_count=F('views_count') + 1)
        store.refresh_from_db(fields=['views_count'])
        return Response({'message': 'Store view recorded', 'views_count': store.views_count})


class LikeStoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        store_id = request.data.get('store_id')
        if not store_id:
            return Response({'errors': [{'msg': 'Store ID is required'}]}, status=400)
        store = get_object_or_404(Store, id=store_id)
        user = request.user
        if store.liked_by.filter(id=user.id).exists():
            store.liked_by.remove(user)
            store.likes = max(0, store.likes - 1)
            store.save(update_fields=['likes'])
            return Response({'message': 'Store unliked', 'isLiked': False, 'likes': store.likes})
        else:
            store.liked_by.add(user)
            store.likes = store.likes + 1
            store.save(update_fields=['likes'])
            return Response({'message': 'Store liked', 'isLiked': True, 'likes': store.likes})


class FollowStoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        store_id = request.data.get('store_id')
        if not store_id:
            return Response({'errors': [{'msg': 'Store ID is required'}]}, status=400)
        store = get_object_or_404(Store, id=store_id)
        user = request.user
        if store.followed_by.filter(id=user.id).exists():
            store.followed_by.remove(user)
            store.followers = max(0, store.followers - 1)
            store.save(update_fields=['followers'])
            return Response({'message': 'Store unfollowed', 'isFollowed': False, 'followers': store.followers})
        else:
            store.followed_by.add(user)
            store.followers = store.followers + 1
            store.save(update_fields=['followers'])
            return Response({'message': 'Store followed', 'isFollowed': True, 'followers': store.followers})


class CommentStoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        store_id = request.data.get('store_id')
        content = request.data.get('content')
        if not store_id:
            return Response({'errors': [{'msg': 'Store ID is required'}]}, status=400)
        if not content:
            return Response({'errors': [{'msg': 'Comment content is required'}]}, status=400)
        store = get_object_or_404(Store, id=store_id)
        user = request.user
        comment = StoreComment.objects.create(
            store=store,
            user=user,
            user_name=user.full_name,
            user_image=user.profile_image.url if getattr(user.profile_image, 'url', None) else None,
            content=content,
        )
        return Response({'message': 'Comment added', 'comment': StoreCommentSerializer(comment).data})


class StoreDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, store_id):
        store = get_object_or_404(Store, id=store_id)
        Store.objects.filter(id=store.id).update(views_count=F('views_count') + 1)
        return Response(StoreSerializer(store).data)


class FavoriteStoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        store_id = request.data.get('store_id')
        if not store_id:
            return Response({'errors': [{'msg': 'Store ID is required'}]}, status=400)
        store = get_object_or_404(Store, id=store_id)
        user = request.user
        if store.favorited_by.filter(id=user.id).exists():
            store.favorited_by.remove(user)
            return Response({'message': 'Store removed from favorites', 'isFavorited': False})
        else:
            store.favorited_by.add(user)
            return Response({'message': 'Store added to favorites', 'isFavorited': True})


class FavoriteStoresListView(generics.ListAPIView):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Store.objects.filter(favorited_by=self.request.user)


class FavoriteStoresByUserView(generics.ListAPIView):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        auth_user = self.request.user
        if str(user_id) != str(auth_user.id) and auth_user.role != 1:
            self.permission_denied(self.request, message='Unauthorized: You can only view your own favorites or must be an admin')
        return Store.objects.filter(favorited_by_id=user_id)


class NearbyStoresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            latitude = float(request.query_params.get('latitude'))
            longitude = float(request.query_params.get('longitude'))
        except (TypeError, ValueError):
            return Response({'errors': [{'msg': 'Latitude and Longitude are required and must be valid numbers'}]}, status=400)
        radius = float(request.query_params.get('radius', 10))
        limit = int(request.query_params.get('limit', 10))

        stores = Store.objects.exclude(user_latitude__isnull=True).exclude(user_longitude__isnull=True).only('id', 'store_name', 'user_latitude', 'user_longitude')
        results = []
        for s in stores:
            dist = haversine_km(latitude, longitude, s.user_latitude, s.user_longitude)
            if dist <= radius:
                results.append({
                    'id': str(s.id),
                    'store_name': s.store_name,
                    'user_latitude': s.user_latitude,
                    'user_longitude': s.user_longitude,
                    'distance_km': round(dist, 2)
                })
        results.sort(key=lambda x: x['distance_km'])
        results = results[:limit]
        if not results:
            return Response({'message': f'No stores found within {radius} km', 'stores': []})
        return Response(results)
