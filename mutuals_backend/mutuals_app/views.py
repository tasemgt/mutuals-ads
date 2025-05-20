import random
from datetime import datetime, date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Interest, Group, SubGroup
from .serializers import InterestSerializer, UserSerializer, GroupSerializer, SubGroupSerializer
from .ml_models.models import assign_new_user_to_cluster, assign_user_to_subgroup 



def calculate_age_and_range(dob_str):
    # Convert dob string (e.g., "1947-05-05") to a date object
    dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    today = date.today()

    # Calculate age
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    # Determine age range
    if age < 18:
        age_range = "Under 18"
    elif 18 <= age <= 25:
        age_range = "18-25"
    elif 26 <= age <= 35:
        age_range = "26-35"
    elif 36 <= age <= 45:
        age_range = "36-45"
    elif 46 <= age <= 55:
        age_range = "46-55"
    elif 56 <= age <= 65:
        age_range = "56-65"
    else:
        age_range = "66+"

    return age, age_range

def generate_unique_user_id():
    while True:
        user_id = f"M{random.randint(1000, 9999)}"
        if not User.objects.filter(user_id=user_id).exists():
            return user_id


# Root route
@api_view(['GET'])
def index(req):
    return Response({'Success': "Setup was successful"})

# ----------------------
# USER VIEWS
# ----------------------


@api_view(['POST'])
def login(request):
    """
    A fake login view that accepts a user_id,
    retrieves the associated user, and returns their data.
    """
    user_id = request.data.get('user_id')

    if not user_id:
        return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(user_id=user_id)
        serializer = UserSerializer(user)
        return Response({
            "message": "Login successful",
            "user": serializer.data
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_user_by_user_id(request, user_id):
    """
    Get detailed user data including group, subgroup, and subgroup members.
    """
    try:
        user = User.objects.select_related('group', 'subgroup').get(user_id=user_id)

        # Build user data response
        user_data = {
            "id": str(user.id),
            "user_id": str(user.user_id),
            "name": user.name,
            "age": user.age,
            "city": user.city,
            "occupation": user.occupation,
            "interests": [
                { "id": str(interest.id), "name": interest.name }
                for interest in user.interests.all()
            ],
            "group": {
                "name": user.group.name if user.group else None,
            },
            "subgroup": {
                "name": user.subgroup.name if user.subgroup else None,
            },
            "subgroupMembers": [],
        }

        # Get subgroup members (excluding current user)
        if user.subgroup:
            members = User.objects.filter(subgroup=user.subgroup).exclude(id=user.id)
            print("Members>", members)
            for member in members:
                user_data["subgroupMembers"].append({
                    "id": str(member.id),
                    "name": member.name,
                    "age": member.age,
                    "occupation": member.occupation,
                })

        return Response(user_data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
def users_handler(request):
    # Gets all users
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    # Create user
    elif request.method == 'POST':
        """
        Creates a user with:
        - Unique user ID
        - Age and age range calculation
        - Group assignment based on interests
        - Subgroup assignment within the group
        """

        # Step 1: Calculate age and age range
        age, age_range = calculate_age_and_range(request.data['dob'])
        request.data['age'] = age
        request.data['age_range'] = age_range

        # Step 2: Generate unique user ID
        request.data['user_id'] = generate_unique_user_id()
        user_id = request.data['user_id']

        # Step 3: Get interests and match to database
        interests = request.data.get('interests', [])  # Expecting a list of interest IDs
        interests_qs = Interest.objects.filter(id__in=interests)
        interest_names = list(interests_qs.values_list('name', flat=True))

        # Step 4: Assign user to a group (cluster) using the interest-based ML algorithm
        cluster_assignment = assign_new_user_to_cluster(user_id, interest_names)

        # Step 5: Use the assigned cluster to get or create the group
        group_id = cluster_assignment.get('cluster')
        if group_id is not None:
            group, _ = Group.objects.get_or_create(group_id=group_id, defaults={"name": f"Group {group_id}"})
            request.data['group_id'] = group.id  # Set foreign key for serializer
        else:
            return Response({"error": "No cluster assigned. Cannot proceed."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 6: Create the user
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Attach interest relations after user is created
            if interests_qs.exists():
                user.interests.set(interests_qs)

            # Step 7: Assign to appropriate subgroup within the assigned group
            assign_user_to_subgroup(user, SubGroup, group)

            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail_handler(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
# ----------------------
# INTEREST VIEWS
# ----------------------

@api_view(['GET', 'POST'])
def interests_handler(request):
    if request.method == 'GET':
        interests = Interest.objects.all()
        serializer = InterestSerializer(interests, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = InterestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------
# GROUP VIEWS
# ----------------------

@api_view(['GET', 'POST'])
def groups_handler(request):
    if request.method == 'GET':
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------
# SUBGROUP VIEWS
# ----------------------

@api_view(['GET', 'POST'])
def subgroups_handler(request):
    if request.method == 'GET':
        subgroups = SubGroup.objects.all()
        serializer = SubGroupSerializer(subgroups, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SubGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)