from rest_framework import viewsets, permissions, generics
from .models import User, Friendship
from .serializers import UserSerializer, FriendshipSerializer
from util.permissions import NoDelete


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    """
    Endpoints is for interacting with a user's data object.

    list:
    Returns a list, containing the current logged in user's object, or empty if the user is not
    logged in.

    create:
    Create a user.

    retrieve:
    Returns current logged in user's object if the right id was passed, else returns an empty list.

    update:
    Updates a user's object, if they are authenticated as that user.

    partial_update:
    Partially updates a user's object, if they are authenticated as that user.

    destroy:
    Deletes a user.
    """

    # This way, an authenticated user can only retrieve, modify or delete its own object.
    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)

    permission_classes = (permissions.AllowAny, )
    serializer_class = UserSerializer


class PendingFriendshipList(generics.ListAPIView):
    """
    Returns Friendships that the user has not reciprocated for the requesting user
    """
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.get_pending_friendships_for_user(user)


class MutualFriendshipList(generics.ListAPIView):
    """
    Returns Mutual Friendships for a user
    """
    # let anyone view anyone else's friends for now, can decide on permission later.
    permission_classes = (permissions.AllowAny, )
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user_id = self.kwargs['user']
        return Friendship.objects.get_mutual_friendships_for_user(user_id)


class FriendshipCreate(generics.CreateAPIView):
    """
    Creates a [one directional] Friendship.
    """
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = FriendshipSerializer
    queryset = Friendship.objects.all()


class DestroyFriendshipPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user


class FriendshipDetail(generics.DestroyAPIView):
    """
    delete:
    Delete's a friendship. If friendship was mutual, will also delete reciprocating friendship.
    """
    permission_classes = (permissions.IsAuthenticated, DestroyFriendshipPermission)
    serializer_class = FriendshipSerializer
    queryset = Friendship.objects.all()

    def perform_destroy(self, instance):
        try:
            mutual_friendship = Friendship.objects.get(
                creator=instance.friend,
                friend=instance.creator
            )
            mutual_friendship.delete()
        except Friendship.DoesNotExist:
            pass
        instance.delete()

