import pyrebase
import pandas as pd
import json


# Firebase configuration
config = {
  "apiKey": "AIzaSyAM25ZltTApK4lsyForPw4donBuM6RWC5E",
  "authDomain": "users-lababerto.firebaseapp.com",
  "databaseURL": "https://users-lababerto-default-rtdb.europe-west1.firebasedatabase.app/",
  "storageBucket": "users-lababerto.appspot.com"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

def import_database_to_csv():
    """Fetch data from Firebase and convert it to CSV format."""
    data = db.get().val()
    if not data:
        return "No data found in the database."
    user_data = db.child("Users").get().val()
    card_data = db.child("Cards").get().val()
    print("USER DATA")
    print(user_data)
    print("CARD DATA")
    print(card_data)
    if not user_data or not card_data:
        return "No data found in the database."
    
    file = open("data.json", "w")
    file.write(json.dumps(user_data, indent=4))
    file.close()
    
    file = open("users.json", "w")
    file.write(json.dumps(card_data, indent=4))
    file.close()   

    
    user_df = pd.DataFrame.from_dict(user_data, orient='index', columns=["UID", "Name", "ID"])
    card_df = pd.DataFrame.from_dict(card_data, orient='index',)

    user_df.to_csv('users.csv', index=False)
    card_df.to_csv('cards.csv', index=False)
    return "Data successfully exported to users.csv and cards.csv"
    
    

import_database_to_csv()    


