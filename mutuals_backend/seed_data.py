import os
import argparse
import json
import django
import pandas as pd
from itertools import islice

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mutuals_backend.settings')  # Replace with your project name
django.setup()

from mutuals_app.models import Interest, User, Group, SubGroup, Event
from mutuals_app.ml_models.models import assign_user_to_subgroup



# csv_file = './data/sm500_data.csv'


def clean_interest_string(raw):
    return [i.strip(" '") for i in raw.split(',') if i.strip(" '")]

# Load Interests to the Database
def load_interests(file_path):
    df = pd.read_csv(file_path)

    # Flatten all interest entries into a list
    all_interests = []

    for entry in df['interests'].dropna():
        # Clean and split on commas
        interests = [i.strip(" '") for i in entry.split(',')]
        all_interests.extend(interests)

    # Get unique interests
    unique_interests = set(all_interests)

    for interest in unique_interests:
        obj, created = Interest.objects.get_or_create(name=interest)
        if created:
            print(f"Added: {interest}")


def load_groups(file_path):
    with open(file_path, 'r') as f:
        group_data = json.load(f)

    for group_id_str, name in group_data.items():
        try:
            group_id = int(group_id_str.strip())
            name = name.strip()
            obj, created = Group.objects.update_or_create(
                group_id=group_id,
                defaults={'name': name}
            )
            if created:
                print(f"Added: {name} (ID: {group_id})")
            else:
                print(f"Updated: {name} (ID: {group_id})")
        except Exception as e:
            print(f"Error processing group {group_id_str}: {e}")


# Load users to the database
def load_users(file_path):
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():  #islice(df.iterrows(), 28, 35, 1):
        user, created = User.objects.get_or_create(
            user_id=row["user_id"],
            defaults={
                "name": row["name"],
                "dob": pd.to_datetime(row["dob"]).date(),
                "gender": row["gender"],
                "city": row["city"],
                "occupation": row["occupation"],
                "budget": float(row["budget"]),
                "age": int(row["age"]),
                "age_range": row["age_range"],
            }
        )

        # Assign interests
        user.interests.clear()
        if pd.notna(row['interests']):
            interest_names = clean_interest_string(row['interests'])
            for name in set(interest_names):
                try:
                    interest = Interest.objects.get(name=name)
                    user.interests.add(interest)
                except Interest.DoesNotExist:
                    continue

        # Assign group from "Cluster" column
        if pd.notna(row["Cluster"]):
            group_id = int(row["Cluster"])
            group, _ = Group.objects.get_or_create(group_id=group_id, defaults={"name": f"Group {group_id}"})
            user.group = group
            user.save()

            # Assign to subgroup
            assign_user_to_subgroup(user, SubGroup, group)

        print(f"{'Created' if created else 'Updated'} user: {user.name}")


def load_events(file_path):
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        try:
            Event.objects.get_or_create(
                event_id=row['event_id'],
                defaults={
                    'event_name': row['event_name'],
                    'event_date': pd.to_datetime(row['event_date']).date(),
                    'location': row['location'],
                    'ticket_price': float(row['ticket_price']),
                    'venue_id': int(row['venue_id']),
                    'tags': eval(row['tags']) if isinstance(row['tags'], str) else row['tags'],
                }
            )
        except Exception as e:
            print(f"Failed to insert row: {row['event_id']} - Error: {e}")


def clear_data():
    User.objects.all().delete()
    SubGroup.objects.all().delete()


def main():
    parser = argparse.ArgumentParser(description="Load data into the database.")
    parser.add_argument('--users', action='store_true', help='Load user data')
    parser.add_argument('--interests', action='store_true', help='Load interest data')
    parser.add_argument('--events', action='store_true', help='Load events data')
    parser.add_argument('--groups', action='store_true', help='Load groups data')
    parser.add_argument('--file', type=str, default='./data/clustered_mutuals.csv', help='Path to CSV file')
    parser.add_argument('--clear', action='store_true', help='Clears data')

    args = parser.parse_args()

    if args.interests:
        load_interests(args.file)
    
    if args.events:
        load_events(args.file)
    
    if args.groups:
        load_groups(args.file)

    if args.users:
        load_users(args.file)
    
    if args.clear:
        clear_data()

    if not args.users and not args.interests:
        parser.print_help()

if __name__ == "__main__":
    main()


#  python seed_data.py --groups --file='./data/groups.json'
#  python seed_data.py --events --file='./data/mock_events.csv'

# python manage.py shell
# from mutuals_app.models import User
# User.objects.all().delete()
