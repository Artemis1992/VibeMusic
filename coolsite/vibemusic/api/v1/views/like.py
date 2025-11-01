# api/v1/views/like.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from vibemusic.models import Post, Track, Comment


class LikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _toggle(self, request, obj):
        """Универсальная функция переключения лайка"""
        user = request.user
        if obj.liked_by.filter(id=user.id).exists():
            obj.liked_by.remove(user)
            return {'liked': False, 'count': obj.liked_by.count()}
        else:
            obj.liked_by.add(user)
            return {'liked': True, 'count': obj.liked_by.count()}

    @action(detail=False, methods=['post'])
    def post(self, request):
        post_id = request.data.get('post_id')
        if not post_id:
            return Response({'error': 'post_id required'}, status=400)
        post = get_object_or_404(Post, id=post_id)
        result = self._toggle(request, post)
        return Response(result)

    @action(detail=False, methods=['post'])
    def track(self, request):
        track_id = request.data.get('track_id')
        if not track_id:
            return Response({'error': 'track_id required'}, status=400)
        track = get_object_or_404(Track, id=track_id)
        result = self._toggle(request, track)
        return Response(result)

    @action(detail=False, methods=['post'])
    def comment(self, request):
        comment_id = request.data.get('comment_id')
        if not comment_id:
            return Response({'error': 'comment_id required'}, status=400)
        comment = get_object_or_404(Comment, id=comment_id)
        result = self._toggle(request, comment)
        return Response(result)