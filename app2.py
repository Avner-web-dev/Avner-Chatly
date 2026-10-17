import streamlit as st

from html import escape

from datetime import datetime

import base64

from supabase import create_client, Client
 
# Initialize Supabase from Streamlit secret

@st.cache_resource

def init_supabase():

    url = st.secrets["SUPABASE_URL"]

    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)
 
supabase = init_supabase()
 
st.set_page_config(page_title="Chatly", layout="centered")
 
#---------- SUPABASE HELPER FUNCTIONS (Placed at the top) ----------
 
def verify_login(username, password):

    try:

        response = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()

        return len(response.data) > 0

    except Exception as e:

        st.error(f"Login check failed {e}")

        return False
 
def register_user(username, password):

    try:

        check = supabase.table("users").select("*").eq("username", username).execute()

        if len(check.data) > 0:

            return False, "Username already exists, please choose a different one."

        # Insert new user

        supabase.table("users").insert({"username": username, "password": password}).execute()

        return True, "Account created successfully"

    except Exception as e:

        # This will show us the exact reason why it failed

        return False, f"Sign up failed: {e}"
 
def get_all_users():

    try:

        response = supabase.table("users").select("username").execute()

        return [user["username"] for user in response.data]

    except Exception:

        st.error("Failed to fetch the users")

        return []
 
def get_messages(user1, user2):

    try:

        response = supabase.table("messages").select("*").execute()

        all_msgs = response.data

        conversation = [

            m for m in all_msgs 

            if (m["sender"] == user1 and m["recipient"] == user2) or 

               (m["sender"] == user2 and m["recipient"] == user1)

        ]

        conversation.sort(key=lambda x: x["id"])

        return conversation

    except Exception as e:

        st.error(f"Error fetching messages: {e}")

        return []
 
def send_message_callback():

    msg = st.session_state.get("message_input", "").strip()

    if msg != "":

        current_user = st.session_state.username

        recipient = st.session_state.selected_user

        current_time = datetime.now().strftime("%I:%M %p")
 
        supabase.table("messages").insert({

            "sender": current_user,

            "recipient": recipient,

            "type": "text",

            "content": msg,

            "time": current_time

        }).execute()
 
        st.session_state.message_input = ""
 
#-load css-

def load_css():

    try:

        with open("style.css") as file:

            css = file.read()

            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    except FileNotFoundError:

        pass
 
load_css()
 
#---------- LOGIN UI ----------

def login_page():

    st.markdown("<h2 style='text-align: center;'>Welcome to Chatly 💬</h2>", unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])

    with tab_login:

        with st.form("login_form"):

            login_user = st.text_input("Username", key="login_username_input").strip()

            login_pass = st.text_input("Password", type="password", key="login_password_input").strip()

            submit_login = st.form_submit_button("Log In", use_container_width=True)

            if submit_login:

                if not login_user or not login_pass:

                    st.warning("Please enter both username and password.")

                elif verify_login(login_user, login_pass):

                    st.session_state.logged_in = True

                    st.session_state.username = login_user

                    st.success("Logged in successfully!")

                    st.rerun()

                else:

                    st.error("Invalid username or password.")
 
    with tab_signup:

        with st.form("signup_form"):

            new_user = st.text_input("Choose Username", key="signup_username_input").strip()

            new_pass = st.text_input("Choose Password", type="password", key="signup_password_input").strip()

            confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm_password_input").strip()

            submit_signup = st.form_submit_button("Create Account", use_container_width=True)

            if submit_signup:

                if not new_user or not new_pass:

                    st.warning("Please fill in all fields.")

                elif new_pass != confirm_pass:

                    st.error("Passwords do not match.")

                else:

                    success, msg = register_user(new_user, new_pass)

                    if success:

                        st.success(msg)

                    else:

                        st.error(msg)
 
#---------- SIDEBAR & NAVIGATION ----------

def sidebar():

    st.sidebar.markdown('<h2>💬 Chatly</h2>', unsafe_allow_html=True)

    st.sidebar.divider()

    st.sidebar.markdown(

        f'''<div class="profile-container">
<div class="avatar">👤</div>
<div>
<b>{escape(st.session_state.username)}</b>
<br>
<small style="color:green">● Online</small>
</div>
</div>''', unsafe_allow_html=True

    )

    st.sidebar.divider()

    menu = st.sidebar.radio("Navigation", ["💬 Chats", "📸 Stories", "👥 Contacts", "⚙️ Settings"], label_visibility="collapsed")

    st.sidebar.divider()

    if st.sidebar.button("🚪 Logout", use_container_width=True):

        st.session_state.logged_in = False

        st.session_state.username = ""

        st.rerun()

    return menu
 
def chat_list():

    st.markdown('<div class="chatlist-header">Chats</div>', unsafe_allow_html=True)

    search = st.text_input("Search", placeholder="Search chats...", label_visibility="collapsed")

    st.write("")

    all_users = get_all_users()

    other_users = [u for u in all_users if u != st.session_state.username]

    for name in other_users:

        if search and search.lower() not in name.lower():

            continue

        col1, col2, col3 = st.columns([1, 3, 1.5], vertical_alignment="center")

        with col1:

            st.markdown('<div class="avatar">👤</div>', unsafe_allow_html=True)

        with col2:

            st.markdown(f'<b>{escape(name)}</b><br><small style="color:#8696a0;">Tap to chat</small>', unsafe_allow_html=True)

        with col3:

            if st.button("Open", key=f"open_{name}", use_container_width=True):

                st.session_state.selected_user = name

                st.rerun()
 
def chat_window():

    recipient = st.session_state.selected_user

    current_user = st.session_state.username
 
    st.markdown(

        f'<div class="chat-header"><div class="chat-header-content"><div class="avatar">👤</div><div>'

        f'<div class="chat-username" style="color: white; font-weight: bold;">{escape(recipient)}</div>'

        f'<div class="online-status" style="color:#00a884;">● Online</div>'

        f'</div></div></div>', unsafe_allow_html=True

    )
 
    messages = get_messages(current_user, recipient)
 
    chat_html = '<div class="chat-area">'

    for msg in messages:

        sender = msg["sender"]

        time = escape(str(msg["time"]))

        msg_type = msg.get("type", "text")
 
        if msg_type == "text":

            message = escape(str(msg.get("content", "")))

            content_html = f'<div class="message-text">{message}</div>'

        elif msg_type == "image":

            content_html = f'<img src="data:image/png;base64,{msg["content"]}" style="max-width: 250px; border-radius: 8px; margin-bottom: 5px;">'

        elif msg_type == "video":

            content_html = f'<video width="250" controls style="border-radius: 8px; margin-bottom: 5px;"><source src="data:video/mp4;base64,{msg["content"]}" type="video/mp4"></video>'
 
        if sender == current_user:

            chat_html += f'<div class="message-wrapper right"><div class="message message-right">{content_html}<div class="message-time">{time} ✓✓</div></div></div>'

        else:

            chat_html += f'<div class="message-wrapper left"><div class="message message-left">{content_html}<div class="message-time">{time}</div></div></div>'
 
    chat_html += "</div>"

    st.markdown(chat_html, unsafe_allow_html=True)

    st.write("")
 
    col1, col2, col3, col4 = st.columns([1, 1, 7, 1])
 
    with col1:

        with st.popover("📎", use_container_width=True):

            st.markdown("**Attach Media**")

            upload_media = st.file_uploader("Upload Image or Video", type=["jpg", "jpeg", "png", "mp4"], label_visibility="collapsed")

            if upload_media:

                if st.button("📤 Send Media", type="primary", use_container_width=True):

                    current_time = datetime.now().strftime("%I:%M %p")

                    file_bytes = upload_media.getvalue()

                    b64_file = base64.b64encode(file_bytes).decode()

                    media_type = "video" if upload_media.name.endswith(".mp4") else "image"
 
                    supabase.table("messages").insert({

                        "sender": current_user,

                        "recipient": recipient,

                        "type": media_type,

                        "content": b64_file,

                        "time": current_time

                    }).execute()

                    st.rerun()
 
    with col2:

        if st.button("😎", key="emoji_button", use_container_width=True):

            st.info("Emoji button clicked")
 
    with col3:

        st.text_input("Message", placeholder=f"Type a message to {recipient}...", label_visibility="collapsed", key="message_input", on_change=send_message_callback)
 
    with col4:

        st.button("➤", key="send_button", use_container_width=True, type="primary", on_click=send_message_callback)
 
def stories():

    st.header("📸 Stories")

    st.caption("Share what is happening around you")

    st.divider()

    if "my_story" not in st.session_state:

        st.session_state.my_story = None
 
    upload_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if upload_file:

        st.image(upload_file, caption="Your story", use_container_width=True)

        if st.button("📤 Post Story", type="primary"):

            st.session_state.my_story = upload_file.getvalue()

            st.success("Story posted successfully")

            st.rerun()
 
def contacts():

    st.header("👥 Contacts")

    st.caption("People you can connect with")

    st.divider()
 
    all_users = get_all_users()

    other_users = [u for u in all_users if u != st.session_state.username]
 
    for name in other_users:

        col1, col2, col3 = st.columns([1, 5, 2], vertical_alignment="center")

        with col1:

            st.markdown('<div class="avatar">👤</div>', unsafe_allow_html=True)

        with col2:

            st.markdown(f'<b>{escape(name)}</b><br><small style="color:#869a0;">Online</small>', unsafe_allow_html=True)

        with col3:

            if st.button("💬 Chat", key=f"chat_{name}", use_container_width=True):

                st.session_state.selected_user = name

                st.rerun()
 
def settings():

    st.header("⚙️ Settings")

    st.caption("Manage your Chatly account")

    st.divider()

    st.subheader("🧑 Profile")

    new_name = st.text_input("Username", value=st.session_state.username)

    st.divider()

    if st.button("🛅 Save settings", type="primary"):

        st.session_state.username = new_name

        st.success("Settings saved ✅ successfully")
 
#---------- SESSION STATE INITIALIZATION ----------

if "message_input" not in st.session_state:

    st.session_state.message_input = ""

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

if "username" not in st.session_state:

    st.session_state.username = ""

if "selected_user" not in st.session_state:

    st.session_state.selected_user = ""
 
#---------- MAIN ROUTING ----------

if not st.session_state.logged_in:

    login_page()

else:

    menu = sidebar()

    if menu == "💬 Chats":

        left, right = st.columns([4, 4], gap="medium")

        with left:

            chat_list()

        with right:

            if st.session_state.selected_user:

                chat_window()

            else:

                st.info("Select a chat from the sidebar to start messaging.")

    elif menu == "📸 Stories":

        stories()

    elif menu == "👥 Contacts":

        contacts()

    else:

        settings()
 
