import os
import argparse
import django
import pandas as pd

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mutuals_backend.settings')  # Replace with your project name
django.setup()

from mutuals_app.models import Interest, User


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


# Load users to the database
def load_users(file_path):
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        # Create or get user
        user, created = User.objects.get_or_create(
            user_id=row['user_id'],
            defaults={
                'name': row['name'],
                'gender': row['gender'],
                'dob': pd.to_datetime(row['dob']).date(),
                'city': row['city'],
                'occupation': row['occupation'],
                'budget': int(row['budget']),
                'age': int(row['age']),
                'age_range': row['age_range'],
            }
        )

        # Always clear previous interests (if updating)
        user.interests.clear()

        # Clean and associate interests
        if pd.notna(row['interests']):
            interest_names = clean_interest_string(row['interests'])
            for name in set(interest_names):
                try:
                    interest = Interest.objects.get(name=name)
                    user.interests.add(interest)
                except Interest.DoesNotExist:
                    print(f"[!] Interest '{name}' not found in DB — skipping.")

        print(f"{'Created' if created else 'Updated'} user: {user.name} with {user.interests.count()} interests.")


def main():
    parser = argparse.ArgumentParser(description="Load data into the database.")
    parser.add_argument('--users', action='store_true', help='Load user data')
    parser.add_argument('--interests', action='store_true', help='Load interest data')
    parser.add_argument('--file', type=str, default='./data/sm500_data.csv', help='Path to CSV file')

    args = parser.parse_args()

    if args.interests:
        load_interests(args.file)

    if args.users:
        load_users(args.file)

    if not args.users and not args.interests:
        parser.print_help()

if __name__ == "__main__":
    main()