import json
import shutil
from user.models import Credentials, AdminCredentials

def drive_health_check():
    username = input("Enter username:")
    email = input("Enter email: ")
    
    check_user = Credentials.objects.filter(
        username=username, email=email).first()
    if check_user is None:
        print("User does not exist")
        return
    
    print(f"Checking drive health for user: {username}")
    print(f"check_user: {check_user}")
    
    check_existing_admin = AdminCredentials.objects.filter(
        admin_username=check_user).first()
    if check_existing_admin is None:
        print("Admin user does not exist")
        return
    
    with open('json/directory.json') as f:
        directory_data = json.load(f)
    if not directory_data:
        print("Directory data is empty")
        return

    drives = []

    for key, path in directory_data.items():
        split_entry = path.split('/')
        drive_name = split_entry[0]
        if drive_name not in drives:
            drives.append(drive_name)

    for drive in drives:
        try:
            usage = shutil.disk_usage(drive)

            total_gb = (usage.total / (1024**3)).__round__(2)
            used_gb = (usage.used / (1024**3)).__round__(2)
            free_gb = (usage.free / (1024**3)).__round__(2)
            percent_full = (used_gb / total_gb * 100).__round__(2)

            print(f"\nDrive: {drive}")
            print(f"Total: {total_gb} GB")
            print(f"Used: {used_gb} GB")
            print(f"Free: {free_gb} GB")
            print(f"Percent full: {percent_full} %")

            if percent_full >= 95:
                print("Drive is 95% full")
            elif percent_full >= 85:
                print("Drive is 85% full")
            elif percent_full >= 70:
                print("Drive is 70% full")
            else:
                print("Drive is healthy ")

        except Exception as e:
            print(f"Error checking drive {drive}: {e}")