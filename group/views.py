from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from .serializers import GroupMemberSerializer, GroupSerializer
from .models import GroupMember, Group


class CreateListDeleteViewSet(viewsets.GenericViewSet,
                              mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.DestroyModelMixin, ):
    pass


class GroupViewSet(viewsets.ModelViewSet):
    """
    API Endpoint containing information on facebook groups.

    create:
    Creates a new group.

    list:
    Returns all groups owned by authenticated user.

    retrieve:
    Returns a specified group if it exists and is owned by authenticated user.

    update:
    Updates a group with specified data if owned by authenticated user.
    The group owner is read-only and will not be
    updated if specified value is different than existing.


    partial_update:
    Partially updates a group with specified data if owned by authenticated user.
    The group is read-only and will not
    be updated if specified value is different than existing.

    delete:
    Deletes a specified group owned by authenticated user and all records of membership for this
    group.

    get_members_by_group:
    Gets list of all members of a group if authenticated user is group owner.

    """
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated,)

    # Use default permissions
    def get_queryset(self):
        return Group.objects.filter(group_owner=self.request.user.id)

    @detail_route(url_path='members-by-group')
    def get_members_by_group(self, request, pk):
        # pylint: disable=unused-argument
        group = Group.objects.get(pk=pk)
        if group.group_owner.id != self.request.user.id:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        else:
            members = GroupMember.objects.filter(group_id=pk)
            serializer = GroupMemberSerializer(members, many=True)
            response = Response(data=serializer.data, status=status.HTTP_200_OK)
        return response


class GroupMemberViewSet(CreateListDeleteViewSet):
    """
    API Endpoint containing information on facebook group members.

    create:
    Adds a user to a group.

    list:
    Returns all groups that user is a member of.

    retrieve:
    Returns a membership record of a group.

    delete:
    Remove user from a group.

    """

    serializer_class = GroupMemberSerializer
    permission_classes = (IsAuthenticated,)

    # Use default permissions. Pulls all members of groups user is owner of or
    # records where user is member
    def get_queryset(self):
        groups = Group.objects.filter(group_owner=self.request.user.id).only('id').all()
        records_as_owner = GroupMember.objects.filter(group_id__in=groups)
        records_as_member = GroupMember.objects.filter(user_id=self.request.user.id)
        return (records_as_member | records_as_owner).distinct()
