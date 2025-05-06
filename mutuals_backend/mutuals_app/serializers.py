from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import User, Interest, Group, SubGroup

class InterestSerializer(ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']

class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'created_at']


class SubGroupSerializer(ModelSerializer):
    group = GroupSerializer(read_only=True)
    class Meta:
        model = SubGroup
        fields = ['id', 'name', 'event', 'group', 'created_at']

# User Serializer
class UserSerializer(ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)  # Show interest names
    interest_ids = PrimaryKeyRelatedField(
        queryset=Interest.objects.all(), many=True, write_only=True, source='interests'
    )

    group = GroupSerializer(read_only=True)
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
            'group',
            'subgroup',
            'interests',
            'interest_ids',  # used for input only
        ]
        # 'interest_ids' is write-only, and 'interests' is read-only to show full names

    def create(self, validated_data):
        """
        Overriding to support M2M creation with interests.
        """
        interests = validated_data.pop('interests', [])
        user = User.objects.create(**validated_data)
        user.interests.set(interests)
        return user

    def update(self, instance, validated_data):
        """
        Overriding to support M2M updates for interests.
        """
        interests = validated_data.pop('interests', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if interests is not None:
            instance.interests.set(interests)
        return instance

        