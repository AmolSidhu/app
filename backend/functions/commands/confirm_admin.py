from user.models import Credentials, AdminCredentials

def confirm_admin():
    username = input("Enter username: ")
    email = input("Enter email: ")
    
    check_user = Credentials.objects.filter(
        username=username, email=email).first()

    if check_user is None:
        print("User does not exists.")
        return
    
    check_existing_admin = AdminCredentials.objects.filter(
        admin_username=check_user).first()
    if check_existing_admin is None:
        print("Admin user does not exists.")
        return
    
    if check_existing_admin.active_admin:
        print("User is already an admin.")
        return
    
    check_existing_admin.active_admin = True
    check_existing_admin.save()
    
    print(f"Admin user {username} confirmed successfully.")