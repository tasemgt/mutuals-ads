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

    # Create user
    elif request.method == 'POST':
        
        age, age_range = calculate_age_and_range(request.data['dob'])
        request.data['age'] = age
        request.data['age_range'] = age_range
        request.data['user_id'] = generate_unique_user_id()

        print(request.data)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Register a fresh user and infer using our model
# @api_view(['POST'])
# @transaction.atomic
# def register_user_and_assign_group(request):
#     """
#     Custom endpoint to register a new user, run ML clustering,
#     and assign them to a group and subgroup.
#     """
#     data = request.data

#     # Validate and temporarily save the user (we'll finalize if clustering succeeds)
#     serializer = UserSerializer(data=data)
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     # --- Step 1: Prepare features for the ML model ---
#     interests = data.get('interests', [])
#     budget = float(data.get('budget', 0))
#     age = int(data.get('age', 0))
    
#     # One-hot encode interests (multi-hot)
#     interest_vector = mlb.transform([interests])  # shape: (1, n_interests)
    
#     # Combine features: [budget, age] + interests
#     feature_vector = np.concatenate([[budget, age], interest_vector[0]])  # shape: (1, total_features)
#     feature_vector = feature_vector.reshape(1, -1)

#     # --- Step 2: Predict the cluster (group ID) ---
#     group_id = ml_model.predict(feature_vector)[0]

#     # --- Step 3: Create or fetch the Group based on cluster ---
#     group, created = Group.objects.get_or_create(name=f"Group-{group_id}")

#     # --- Step 4: Find or create a suitable SubGroup ---
#     # For now, we keep a simple rule: 5 users per subgroup max
#     subgroup_qs = SubGroup.objects.filter(group=group)
#     assigned_subgroup = None
#     for subgroup in subgroup_qs:
#         if subgroup.users.count() < 5:
#             assigned_subgroup = subgroup
#             break

#     # If all subgroups are full or none exist, create a new one
#     if not assigned_subgroup:
#         assigned_subgroup = SubGroup.objects.create(name=f"{group.name}-Subgroup-{subgroup_qs.count() + 1}", group=group)

#     # --- Step 5: Create and save the user with group/subgroup ---
#     user = serializer.save(group=group, subgroup=assigned_subgroup)

#     # Assign the user to the subgroup (M2M)
#     assigned_subgroup.users.add(user)

#     return Response({
#         "message": "User registered and assigned to group/subgroup.",
#         "user": UserSerializer(user).data,
#         "group": group.name,
#         "subgroup": assigned_subgroup.name
#     }, status=status.HTTP_201_CREATED)


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