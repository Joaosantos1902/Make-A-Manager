import streamlit as st
import Prusa_Stats as ps
import PrusaStats_TV as pstv
import time
import pyrebase as fb
import Switch_Stats as sws


config = {
    "apiKey": "AIzaSyAM25ZltTApK4lsyForPw4donBuM6RWC5E",
    "databaseURL": "https://users-lababerto-default-rtdb.europe-west1.firebasedatabase.app/",
    "authDomain": "users-lababerto.firebaseapp.com",
    "projectId": "users-lababerto",
    "storageBucket": "users-lababerto.appspot.com",

    # Se usares autenticação com certificado:
    # "serviceAccount": "caminho/para/firebase-key.json"
}

firebase = fb.initialize_app(config)
auth = firebase.auth()

if "user" not in st.session_state:
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.session_state.page = "home"  # Define a página inicial após login
            st.rerun()  # Reinicia a app com o utilizador autenticado
        except Exception as e:
            st.error("Login falhou. Verifica as credenciais ou tenta mais tarde.")
    st.stop()  # Para execução até login ser bem-sucedido
else:
    user = st.session_state.user

db = firebase.database()
# Navigation buttons
def go_to_home():
    st.session_state.page = "home"

def go_to_stats_month():
    st.session_state.page = "stats_month"

def go_to_stats_week():
    st.session_state.page = "stats_week"

def go_to_registration():
    st.session_state.page = "registration"

def got_to_week_TV():
    st.session_state.page = "stats_week_TV"

def go_to_month_TV():
    st.session_state.page = "stats_month_TV"

def go_to_switch_stats():
    st.session_state.page = "stats_Switch"

def go_to_card(username, employee_id):
    st.session_state.page = "card"
    st.session_state.username = username
    st.session_state.employee_id = employee_id


    

# Sidebar or main page buttons
st.sidebar.button("🏠 Home", on_click=go_to_home)
st.sidebar.button("Switch Stats", on_click=go_to_switch_stats)
st.sidebar.button("ℹ️ Month Stats", on_click=go_to_stats_month)
st.sidebar.button("📊 Week Stats", on_click=go_to_stats_week)
st.sidebar.button("🆕 Register User", on_click=go_to_registration)
st.sidebar.button("📺 Week Stats TV", on_click=got_to_week_TV)
st.sidebar.button("📺 Month Stats TV", on_click=go_to_month_TV)

# Display content based on selected page
if st.session_state.page == "home":
    st.title("Home Page")
    st.write("Welcome to the home page. Choose an option from the buttons below.")
    if st.button("Go to Week Stats"):
        go_to_stats_week()
        st.rerun()  # Restart the app to reset the state
    if st.button("Go to Week Stats TV"):
        got_to_week_TV()
        st.rerun()  # Restart the app to reset the state
    if st.button("Go to Month Stats"):
        go_to_stats_month()
        st.rerun()  # Restart the app to reset the state
    if st.button("Go to Month Stats TV"):
        go_to_month_TV()
        st.rerun()  # Restart the app to reset the state
    if st.button("Register a new User"):
        go_to_registration()
        st.rerun()  # Restart the app to reset the state

elif st.session_state.page == "stats_Switch":
    st.set_page_config(
        page_title="Switch Stats Month",
        layout="wide",  # This enables wide mode
        initial_sidebar_state="collapsed"
    )

    st.title("IStartLab Switch Stats Month")

    switch_stats, switch_user_stats = sws.getStats_month()

    st.write("Switch Stats:")
    st.write(switch_stats)
    st.write("Switch Usage per User:")
    st.write(switch_user_stats)

    
    if st.button("Back to Home"):
        go_to_home()
        st.rerun()


    time.sleep(3600)

    st.rerun()

elif st.session_state.page == "stats_week_TV":

    st.set_page_config(
        page_title="Prusa Stats Week TV",
        layout="wide",  # This enables wide mode
        initial_sidebar_state="collapsed"
    )

    st.title("LabAberto Printer Stats Week")

    prusatv_stats = pstv.getStats_week()



    

   
    st.write("PRUSA TV Stats:")
    st.write(ps.printer_stats(prusatv_stats))
    st.write("Number of Prints:")
    st.write(ps.number_of_prints(prusatv_stats))
    st.write("PRUSA TV Usage per User:")
    st.write(ps.filter_and_count_status(prusatv_stats, "PRINTING"))
    st.write("PRUSA TV Error Stats per User:")
    st.write(ps.filter_and_count_status(prusatv_stats, "ERROR"))
    st.write("PRUSA TV Attention Stats per User:")
    st.write(ps.filter_and_count_status(prusatv_stats, "ATTENTION"))
    
    if st.button("Back to Home"):
        go_to_home()
        st.rerun()


    time.sleep(3600)

    st.rerun()
elif st.session_state.page == "stats_week":

    st.set_page_config(
        page_title="Prusa Stats Week",
        layout="wide",  # This enables wide mode
        initial_sidebar_state="collapsed"
    )

    st.title("IStartLab Printer Stats Week")

    prusa4_stats, prusa5_stats, prusa6_stats = ps.getStats_week()

    # Cria as 3 colunas lado a lado
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("PRUSA 4 Stats:")
        st.write(ps.printer_stats(prusa4_stats))
        st.write("PRUSA 4 Usage per User:")
        st.write(ps.filter_and_count_status(prusa4_stats, "PRINTING"))
        st.write("PRUSA 4 Error Stats per User:")
        st.write(ps.filter_and_count_status(prusa4_stats, "ERROR"))
        st.write("PRUSA 4 Attention Stats per User:")
        st.write(ps.filter_and_count_status(prusa4_stats, "ATTENTION"))
    with col2:
        st.write("PRUSA 5 Stats:")
        st.write(ps.printer_stats(prusa5_stats))
        st.write("PRUSA 5 Usage per User:")
        st.write(ps.filter_and_count_status(prusa5_stats, "PRINTING"))
        st.write("PRUSA 5 Error Stats per User:")
        st.write(ps.filter_and_count_status(prusa5_stats, "ERROR"))
        st.write("PRUSA 5 Attention Stats per User:")
        st.write(ps.filter_and_count_status(prusa5_stats, "ATTENTION"))
    with col3:
        st.write("PRUSA 6 Stats:")
        st.write(ps.printer_stats(prusa6_stats))
        st.write("PRUSA 6 Usage per User:")
        st.write(ps.filter_and_count_status(prusa6_stats, "PRINTING"))
        st.write("PRUSA 6 Error Stats per User:")
        st.write(ps.filter_and_count_status(prusa6_stats, "ERROR"))
        st.write("PRUSA 6 Attention Stats per User:")
        st.write(ps.filter_and_count_status(prusa6_stats, "ATTENTION"))

    if st.button("Back to Home"):
        go_to_home()
        st.rerun()


    time.sleep(3600)

    st.rerun()

elif st.session_state.page == "stats_month":

    st.set_page_config(
        page_title="Prusa Stats Month",
        layout="wide",  # This enables wide mode
        initial_sidebar_state="collapsed"
    )

    st.title("IStartLab Printer Stats Month")

    prusa4_stats, prusa5_stats, prusa6_stats = ps.getStats_month()

    # Cria as 3 colunas lado a lado
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("PRUSA 4 Stats:")
        st.write(ps.printer_stats(prusa4_stats))
        st.write("Number of Prints:")
        st.write(ps.number_of_prints(prusa4_stats))
        st.write("PRUSA 4 Usage per User:")
        st.write(ps.filter_and_count_status(prusa4_stats, "PRINTING"))
        st.write("PRUSA 4 Error Stats per User:")
        st.write(ps.filter_and_count_status(prusa4_stats, "ERROR"))
        st.write("PRUSA 4 Attention Stats per User:")
        st.write(ps.filter_and_count_status(prusa4_stats, "ATTENTION"))
    with col2:
        st.write("PRUSA 5 Stats:")
        st.write(ps.printer_stats(prusa5_stats))
        st.write("Number of Prints:")
        st.write(ps.number_of_prints(prusa5_stats))
        st.write("PRUSA 5 Usage per User:")
        st.write(ps.filter_and_count_status(prusa5_stats, "PRINTING"))
        st.write("PRUSA 5 Error Stats per User:")
        st.write(ps.filter_and_count_status(prusa5_stats, "ERROR"))
        st.write("PRUSA 5 Attention Stats per User:")
        st.write(ps.filter_and_count_status(prusa5_stats, "ATTENTION"))
    with col3:
        st.write("PRUSA 6 Stats:")
        st.write(ps.printer_stats(prusa6_stats))
        st.write("Number of Prints:")
        st.write(ps.number_of_prints(prusa6_stats))
        st.write("PRUSA 6 Usage per User:")
        st.write(ps.filter_and_count_status(prusa6_stats, "PRINTING"))
        st.write("PRUSA 6 Error Stats per User:")
        st.write(ps.filter_and_count_status(prusa6_stats, "ERROR"))
        st.write("PRUSA 6 Attention Stats per User:")
        st.write(ps.filter_and_count_status(prusa6_stats, "ATTENTION"))

    if st.button("Back to Home"):
        go_to_home()
        st.rerun()


    time.sleep(3600)

    st.rerun()

elif st.session_state.page == "stats_month_TV":

    st.set_page_config(
        page_title="Prusa Stats Month TV",
        layout="wide",  # This enables wide mode 
        initial_sidebar_state="collapsed"
    )

    st.title("LabAberto Printer Stats Month")

    prusatv_stats = pstv.getStats_month()



    st.write("PRUSA TV Stats:")
    st.write(ps.printer_stats(prusatv_stats))
    st.write("Number of Prints:")
    st.write(ps.number_of_prints(prusatv_stats))
    st.write("PRUSA TV Usage per User:")
    st.write(ps.filter_and_count_status(prusatv_stats, "PRINTING"))
    st.write("PRUSA TV Error Stats per User:")
    st.write(ps.filter_and_count_status(prusatv_stats, "ERROR"))
    st.write("PRUSA TV Attention Stats per User:")
    st.write(ps.filter_and_count_status(prusatv_stats, "ATTENTION"))
    
    if st.button("Back to Home"):
        go_to_home()
        st.rerun()


    time.sleep(3600)

    st.rerun()

elif st.session_state.page == "registration":
    st.title("User Registration")
    st.write("This is the registration page. Here you can register a new user.")
    
    # Example form for user registration
    with st.form("registration_form"):
        username = st.text_input("Name")
        employee_id = st.text_input("Employee ID")
        submit_button = st.form_submit_button("Register Card")


        if submit_button:
            # Here you would handle the registration logic
            db.child("UID").set("00000FFFFF")
            go_to_card(username, employee_id)
            st.rerun()  # Restart the app to reset the state
    
    if st.button("Back to Home"):
        go_to_home()
        st.rerun()

elif st.session_state.page == "card":
    st.title("User Card Registration")
    st.write(f"Username: {st.session_state.username}")
    st.write(f"Employee ID: {st.session_state.employee_id}")

    st.write("Please tap your card to register it.")

     # Here you can add more functionality related to the user card
    
    if st.button("Back to Home"):
        go_to_home()
        st.rerun()  # Restart the app to reset the state
    
    elif st.button("Back to Registration"):
        go_to_registration()
        st.rerun()  # Restart the app to reset the state


    while db.child("UID").get().val() == "00000FFFFF":
        time.sleep(1)

    UID = db.child("UID").get().val()
    final_UID = UID.replace(" ", "").upper()
    st.write(f"Card UID: {UID}")

    if db.child("Users").child(final_UID).get().val():
        st.error("This card is already registered. Please use a different card.")
        db.child("UID").set("00000FFFFF")  # Reset UID for next registration
        time.sleep(2)
        st.rerun()  # Restart the app to allow for a new registration
    else:
        # Save user data to Firebase
        db.child("Cards").child(final_UID).set({
            "Name": st.session_state.username,
            "Employee ID": st.session_state.employee_id,
        })

        db.child("Users").child(st.session_state.employee_id).set({
            "Name": st.session_state.username,
            "UID": final_UID
        })
        st.success("Card registered successfully!")
        time.sleep(2)
        go_to_registration()
        st.rerun()
    




    
    
   
    
