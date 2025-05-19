import joblib
import os
import random
from datetime import datetime, date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import User, Interest, Group, SubGroup
from .serializers import InterestSerializer, UserSerializer, GroupSerializer, SubGroupSerializer
import numpy as np
from .ml_models.models import assign_new_user_to_cluster 


# Load your trained clustering model (e.g., KMeans)
# MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'clustering_model.pkl')
# ml_model = joblib.load(MODEL_PATH)

# # Pre-trained encoder to match training-time format for interests
# mlb = joblib.load(os.path.join(os.path.dirname(__file__), 'ml_models', 'interest_encoder.pkl'))


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
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Calculate age and age range
        age, age_range = calculate_age_and_range(request.data['dob'])
        request.data['age'] = age
        request.data['age_range'] = age_range

        # Generate unique user ID
        request.data['user_id'] = generate_unique_user_id()

        # Assign user to a group (cluster) using their interests
        interests = request.data.get('interests', [])  # This should be a list of strings
        user_id = request.data['user_id']

        # Lookup interest names in the database
        interests_qs = Interest.objects.filter(id__in=interests)
        interest_names = list(interests_qs.values_list('name', flat=True)) 

        print(user_id)

        cluster_assignment = assign_new_user_to_cluster(user_id, interest_names)

        print("Cluster>>", cluster_assignment)

        # Add the cluster as group_id to the user data
        if cluster_assignment['cluster'] is not None:
            request.data['group_id'] = cluster_assignment['cluster']
        else:
            request.data['group_id'] = None  # Or set a default group if needed

        # Proceed with serializer
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# def users_handler(request):
#     if request.method == 'GET':
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)

#     # Create user
#     elif request.method == 'POST':
        
#         age, age_range = calculate_age_and_range(request.data['dob'])
#         request.data['age'] = age
#         request.data['age_range'] = age_range
#         request.data['user_id'] = generate_unique_user_id()

#         print(request.data)

#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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