import streamlit as st
from html import escape
from datetime import datetime
import base64
st.set_page_config(page_title="Login",layout="centered")
#-load css-
def load_css():
    file=open("style.css")
    css=file.read()
    #link the css to our application
    st.markdown(f"<style>{css}</style>",unsafe_allow_html=True)
load_css()
#----------login ui----------
#display the login heading
def login_page():
    st.markdown('<h1>Login</h1>',unsafe_allow_html=True)
    #display a description message
    st.markdown('<div class="login-description">'
                'Please enter your login details'
                '</div>',unsafe_allow_html=True)
    username=st.text_input("Username",placeholder="Enter your username")
    password=st.text_input("Password",placeholder="Enter your password",type="password")
    if st.button("Submit"):
        if username=="":
            st.warning("Fill in the username")
        elif password=="":
            st.warning("Fill in the password")
        else:
            file=open("C:/Users/mjkal/OneDrive/Documents/streamlit/chatting_app/Data_base.txt")
            data=file.readlines()
            flag=0
            for i in data:
                u,p=i.strip().split(",")
                if username==u and password==p:
                    flag=1
                    st.success("Login successful")
                    st.session_state.logged_in=True
                    st.session_state.username=username
                    st.rerun()
                    break
            if flag==0:
                st.warning("Username or password does not exsits")
#----------session state----------
if "message_input" not in st.session_state:
    st.session_state.message_input=""
if "my_story" not in st.session_state:
    st.session_state.my_story=None
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
if "username" not in st.session_state:
    st.session_state.username=""
if "selected_user" not in st.session_state:
    st.session_state.selected_user="Avner"
if "messages" not in st.session_state:
    st.session_state.messages={
        "Aarav": [
 
{"sender": "Aarav", "message": "Hey! How are you?", "time": "10:30 AM"},
 
        {"sender": "Me", "message": "I am good! What about you?", "time": "10:32 AM"},
 
        {"sender": "Aarav", "message": "Doing great 😄", "time": "10:33 AM"}
 
    ],
 
    "Riya": [{"sender": "Riya", "message": "Did you complete the project?", "time": "9:45 AM"}],
 
    "Rahul": [{"sender": "Rahul", "message": "Let's meet tomorrow.", "time": "Yesterday"}],
 
    "Ananya": [{"sender": "Ananya", "message": "Check this photo 😂", "time": "Yesterday"}]
 
        }
#------------------sidebar-------------------
def sidebar():
    st.sidebar.markdown('<h2>💬Chatly</h2>',unsafe_allow_html=True)
    st.sidebar.divider()
    st.sidebar.markdown(
        f'''<div class="profile-container">
        <div class="avatar">👤</div>
        <div>
        <b>{escape(st.session_state.username)}</b>
        <br>
        <small style="color:green">●Online</small>
        </div>
        </div>
        ''',unsafe_allow_html=True
        )
    st.sidebar.divider()
    menu=st.sidebar.radio("Navigation",["💬Chats","📸 Stories", "👥 Contacts", "⚙️ Settings"],label_visibility="collapsed")
    st.sidebar.divider()
    if st.sidebar.button("🚪logout",use_container_width=True):
        st.session_state.logged_in=False
        st.session_state.username=""
        st.rerun()
    return menu
def chat_list():
    st.markdown('<div class="chatlist-header">Chats</div>',unsafe_allow_html=True)
    search=st.text_input("Search",placeholder="Search chats...",label_visibility="collapsed")
    st.write("")
    user=[
        ("Aarav","😎","How's your day?"),
        ("Riya","🥳","I am good!"),
        ("Rahul","😅","Hi"),
        ("Ananya","😭","Hello")
        ]
    for name,avatar,last_message in user:
        if (search) and (search.lower() not in name.lower()):
            continue
        col1,col2,col3=st.columns([1,3,1.5],vertical_alignment="center")
        with col1:
            st.markdown(f'<div class="avatar">{avatar}</div>',unsafe_allow_html=True)
        with col2:
            st.markdown(f'<b>{escape(name)}</b><br><small style="color:#8696a0;">{escape(last_message)}</small>',unsafe_allow_html=True)
        with col3:
            if st.button("open",key=f"open_{name}",use_container_width=True):
                st.session_state.selected_user=name
                st.rerun()
#chat window
def send_message_callback():
    msg=st.session_state.get("message_input","").strip()
    if msg!="":
        user=st.session_state.selected_user
        current_time=datetime.now().strftime("%I:%M %p")
        if user not in st.session_state.messages:
            st.session_state.messages[user]=[]
        st.session_state.messages[user].append({"sender":"Me","type":"text","message":msg,"time":current_time})
        st.session_state.message_input=""
def stories():
    st.header("📸 Stories")
    st.caption("Share what is happening around you")
    st.divider()
    col=st.columns(5)
    if st.session_state.my_story:
        image=base64.b64encode(st.session_state.my_story).decode()
        icon=f'<img src="data: image/png;base64,{image}" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">'
    else:
        icon="+"
    stories_data=[(icon,"Your stories"),("😎","Aarav"),("🥳","Riya"),("😅","Rahul"),("😭","Ananya")]
    for col,(avatar,name) in zip(col,stories_data):
       with col:
           st.markdown(f'<div class="story"><div class="story-avatar">{avatar}</div><b>{escape(name)}</b></div>',unsafe_allow_html=True)
    st.divider()
    st.subheader("Upload Story")
    upload_file=st.file_uploader("Choose an image",type={"jpg","jpeg","png"},label_visibility="collapsed")
    if upload_file:
        st.image(upload_file,caption="Your story",use_container_width=True)
        if st.button("📤 Post Story",type="primary"):
            st.session_state.my_story=upload_file.getvalue()
            st.success("Story posted successfully")
            st.rerun()
def chat_window():
    user=st.session_state.selected_user
    st.markdown(
        f'<div class="chat-header"><div class="chat-header-content"><div class="avatar">😭</div><div>'
        f'<div class="chat-username">{escape(user)}</div><div class="online-staus" style="color:#00a884;">●Online</div>'
        f'</div></div></div>',unsafe_allow_html=True
        )
    chat_html='<div class="chat-area">'
    messages=st.session_state.messages.get(user,[])
    for msg in messages:
        sender=msg["sender"]
        time=escape(str(msg["time"]))
        msg_type=msg.get("type","text")
        if msg_type=="text":
           message=escape(str(msg.get("message","")))
           content_html=f'<div class="message-text">{message}</div>'
        elif msg_type=="image":
            content_html = f'<img src="data:image/png;base64,{msg["content"]}" style="max-width: 250px; border-radius: 8px; margin-bottom: 5px;">'
        elif msg_type=="video":
            content_html = f'<video width="250" controls style="border-radius: 8px; margin-bottom: 5px;"><source src="data:video/mp4;base64,{msg["content"]}" type="video/mp4"></video>'
        if sender!="Me":
            chat_html+=f'<div class="message-wrapper left"><div class="message message-left"><div class="message-text">{content_html}</div><div class="message-time">{time}</div></div></div>'
        else:
            chat_html+=f'<div class="message-wrapper right"><div class="message message-right"><div class="message-text">{content_html}</div><div class="message-time">{time}✓✓</div></div></div>'
    chat_html+="</div>"
    st.markdown(chat_html,unsafe_allow_html=True)
    st.write("")
    col1,col2,col3=st.columns([1,8,1])
    with col1:
        if st.button("😎",key="emoji_button",use_container_width=True):
            st.info("Emoji sent")
    with col2:
        st.text_input("Message",placeholder=f"Type a message to {user}...",label_visibility="collapsed",key="message_input",on_change=send_message_callback)
    with col3:
        st.button("➤",key="send_button",use_container_width=True,type="primary",on_click=send_message_callback)
    with st.expander("attach image or video"):
        upload_media=st.file_uploader("Choose a file",type=["jpg","jpeg","png","mp4"],label_visibility="collapsed")
        if upload_media:
            if st.button("Send Media",type="primary"):
                current_time=datetime.now().strftime("%I:%M %p")
                file_bites=upload_media.getvalue()
                b64_file=base64.b64encode(file_bites).decode()
                #determine image or video
                media_type="video" if upload_media.name.endswith(".mp4") else "image"
                if user not in st.session_state.messages:
                    st.session_state.messages[user]=[]
                st.session_state.messages[user].append({
                    "sender":"Me",
                    "type":media_type,
                    "content":b64_file,
                    "time":current_time,
                    })
                st.rerun()
def contacts():
    st.header("👥 Contacts")
    st.caption("People you can connect with")
    st.divider()
    contacts_data=[
        ("Aarav","😎","Online"),
        ("Riya","🥳","Online"),
        ("Rahul","😅","Offline"),
        ("Ananya","😭","Offline")
        ]
    for name,avatar,status in contacts_data:
        col1,col2,col3=st.columns([1,5,2],vertical_alignment="center")
        with col1:
            st.markdown(f'<div class="avatar">{avatar}</div>',unsafe_allow_html=True)
        with col2:
            st.markdown(f'<b>{escape(name)} </b><br><small style="color:#869a0;">{status}</small>',unsafe_allow_html=True)
        with col3:
            if status=="Online":
                if st.button("💬Chat",key=f"chat_{name}",use_container_width=True):
                    st.session_state.selcted_user=name
                    st.rerun()
            else:
                st.button("Offline",key=f"Offline_{name}",disabled=True,use_container_width=True)
def settings():
    st.header("⚙ Settings")
    st.caption("Manage your chatly account")
    st.divider()
    st.subheader("🧑 Profile")
    username=st.text_input("Username",value=st.session_state.username)
    about=st.text_area("About",value="Hey there, I'm using chatly.")
    st.divider()
    st.subheader("🔏 Privacy and notifications")
    st.checkbox("Show online status",value=True)
    st.checkbox("Read receipts",value=True)
    st.checkbox("Notifications",value=True)
    st.divider()
    if st.button("🛅 Save settings",type="primary"):
        st.session_state.username=username
        st.success("Settings saved ✅ successfully")
#--------main code--------
if st.session_state.logged_in==False:
    login_page()
else:
    menu=sidebar()
    if menu=="💬Chats":
        left,right=st.columns([4,4],gap="medium")
        with left:
            chat_list()
        with right:
            chat_window()
    elif menu=="📸 Stories":
        stories()
    elif menu=="👥 Contacts":
        contacts()
    else:
        settings()