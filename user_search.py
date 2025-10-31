import pyrebase

# Firebase configuration
config = {
  "apiKey": "",
  "authDomain": "",
  "databaseURL": "",
  "storageBucket": ""
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

def search_user_by_id(user_id):
    """Search for a user in the Firebase database by their ID."""
    user = db.child("Users").child(user_id).get().val()
    user_name = user['Name'] if user else "User not found"
    user_UID = user['UID'] if user else "N/A"
    
    
    return user_name, user_UID

def seach_user_by_card_UID(card_UID):
    """Search for a user in the Firebase database by their Card UID."""
    card = db.child("Cards").child(card_UID).get().val()
    user_name = card['Name'] if card else "Card not found"
    user_ID = card['Employee ID'] if card else "N/A"

    return user_name, user_ID

user_name_by_id, user_UID_by_ID  = search_user_by_id("Test1")

user_name_by_card, user_ID_by_card = seach_user_by_card_UID("A738G3V6")

print(f"Search by ID: Name: {user_name_by_id}, UID: {user_UID_by_ID}")
print(f"Search by Card UID: Name: {user_name_by_card}, ID: {user_ID_by_card}")