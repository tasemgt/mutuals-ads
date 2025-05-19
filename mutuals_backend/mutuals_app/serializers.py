from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SlugRelatedField
from .models import User, Interest, Group, SubGroup

class InterestSerializer(ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']

class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'group_id', 'name', 'created_at']


class SubGroupSerializer(ModelSerializer):
    group = GroupSerializer(read_only=True)
    class Meta:
        model = SubGroup
        fields = ['id', 'subgroup_id', 'name', 'event', 'group', 'created_at']


class UserSerializer(ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)
    interest_ids = PrimaryKeyRelatedField(
        queryset=Interest.objects.all(), many=True, write_only=True, source='interests'
    )

    # Group handling
    group = GroupSerializer(read_only=True)  # Show group data
    group_id = SlugRelatedField(  # Accept group_id for assignment
        slug_field='group_id',
        queryset=Group.objects.all(),
        source='group',
        write_only=True,
        required=False
    )

    # Subgroup handling (read-only)
    subgroup = SubGroupSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'user_id',
            'gender',
            'dob',
            'city',
            'occupation',
            'budget',
            'age',
            'age_range',
            'group',        # full group data
            'group_id',     # for input only
            'subgroup',
            'interests',
            'interest_ids',
        ]

    def create(self, validated_data):
        interests = validated_data.pop('interests', [])
        user = User.objects.create(**validated_data)
        user.interests.set(interests)
        return user

    def update(self, instance, validated_data):
        interests = validated_data.pop('interests', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if interests is not None:
            instance.interests.set(interests)
        return instance

        