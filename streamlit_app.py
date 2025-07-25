import datetime
import streamlit as st
import pandas as pd
import requests
import json
import time
import base64
from io import BytesIO
from PIL import Image

from app import get_db

import joblib
from sklearn.pipeline import Pipeline

# Add this at the top of your streamlit_app.py
# st.markdown("""
#     <style>
#         /* Clear floats after message containers */
#         .message-container {
#             clear: both;
#             margin-bottom: 10px;
#         }
        
#         /* Sender's message styling */
#         .sender-message {
#             padding: 8px 12px;
#             border-radius: 15px;
#             margin-left: auto;
#             margin-right: 0;
#             max-width: 70%;
#             float: right;
#             text-align: left;
#         }
        
#         /* Receiver's message styling */
#         .receiver-message {
#             padding: 8px 12px;
#             border-radius: 15px;
#             margin-right: auto;
#             margin-left: 0;
#             max-width: 70%;
#             float: left;
#             color: #333;
#             background-color: #f1f1f1;
#             text-align: left;
#         }
        
#         /* Message time styling */
#         .message-time {
#             font-size: 0.7em;
#             color: #666;
#             margin-top: 3px;
#         }
        
#         /* Right-aligned time for sender */
#         .sender-time {
#             text-align: right;
#         }
        
#         /* Left-aligned time for receiver */
#         .receiver-time {
#             text-align: left;
#         }
#     </style>
# """, unsafe_allow_html=True)

# ----- Backend API Configuration -----
API_BASE_URL = "https://project-test-ii.onrender.com/"  # Replace with your Flask backend URL

# ----- Session State Initialization -----
if 'user' not in st.session_state:
    st.session_state.user = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'page' not in st.session_state:
    st.session_state.page = "login"

# ----- Helper Functions -----
def call_api(endpoint, method="GET", data=None):
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}/{endpoint}")
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data)
        elif method == "PUT":
            response = requests.put(f"{API_BASE_URL}/{endpoint}", json=data)
        elif method == "DELETE":
            response = requests.delete(f"{API_BASE_URL}/{endpoint}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# ----- Yield Prediction Tab -----
def yield_prediction_tab():
    st.title("🌽 Corn Yield Prediction")
    
    # Load the trained model and encoders
    try:
        model = joblib.load('corn_yield_predictor.pkl')
        label_encoders = joblib.load('label_encoders.pkl')
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return
    
    with st.form("yield_prediction_form"):
        st.subheader("Enter Farm Details")
        
        # Numerical inputs
        col1, col2 = st.columns(2)
        with col1:
            acreage = st.number_input("Acreage (acres)", min_value=0.1, max_value=20.0, value=2.0)
            fertilizer = st.number_input("Fertilizer Amount (kg)", min_value=0, max_value=500, value=50)
        with col2:
            laborers = st.number_input("Number of Laborers", min_value=1, max_value=10, value=2)
            household_size = st.number_input("Household Size", min_value=1, max_value=15, value=5)
        
        # Categorical inputs
        education = st.selectbox("Education Level", ["Primary", "Secondary", "Certificate", "Diploma", "Degree"])
        gender = st.selectbox("Gender", ["Male", "Female"])
        age_bracket = st.selectbox("Age Bracket", ["18-35", "36-45", "46-55", "56-65", "above 65"])
        water_source = st.selectbox("Water Source", ["Rain", "Irrigation", "Other"])
        credit_source = st.selectbox("Main Credit Source", ["Credit groups", "Savings", "Family", "Other"])
        advisory_lang = st.selectbox("Advisory Language", ["Kiswahili", "English", "Vernacular"])
        
        if st.form_submit_button("Predict Yield"):
            # Create input DataFrame
            input_data = pd.DataFrame({
                'Acreage': [acreage],
                'Fertilizer amount': [fertilizer],
                'Laborers': [laborers],
                'Education': [education],
                'Gender': [gender],
                'Age bracket': [age_bracket],
                'Household size': [household_size],
                'Water source': [water_source],
                'Main credit source': [credit_source],
                'Advisory language': [advisory_lang]
            })
            
            # Encode categorical variables
            for col in label_encoders:
                if col in input_data.columns:
                    input_data[col] = label_encoders[col].transform(input_data[col])
            
            # Make prediction
            try:
                prediction = model.predict(input_data)
                st.success(f"### Predicted Yield: **{prediction[0]:.2f} kg**")
                
                # Show interpretation
                if prediction[0] < 200:
                    st.warning("Low yield expected. Consider improving fertilizer use or irrigation.")
                elif prediction[0] > 400:
                    st.balloons()
                    st.success("High yield expected! Optimal farming conditions.")
                
            except Exception as e:
                st.error(f"Prediction failed: {str(e)}")

def messages_tab():
    st.title("💬 Messages")
    
    # Add custom CSS for WhatsApp-like styling
    st.markdown("""
    <style>
        /* WhatsApp-like message bubbles */
        .message-container {
            clear: both;
            margin-bottom: 8px;
        }
        
        .sender-message {
            background-color: #ffffff;
            color: #333;
            border: 1px solid #d9d9d9;
            border-radius: 7.5px 0 7.5px 7.5px;
            padding: 8px 12px;
            margin-left: auto;
            margin-right: 0;
            max-width: 70%;
            min-width: min-content;
            width: fit-content;
            word-wrap: break-word;
            position: relative;
            box-shadow: 0 1px 0.5px rgba(0,0,0,0.1);
        }
        
        .receiver-message {
            background-color: #ffffff;
            color: #333;
            border: 1px solid #d9d9d9;
            border-radius: 0 7.5px 7.5px 7.5px;
            padding: 8px 12px;
            margin-right: auto;
            margin-left: 0;
            max-width: 70%;
            min-width: min-content;
            width: fit-content;
            word-wrap: break-word;
            position: relative;
            box-shadow: 0 1px 0.5px rgba(0,0,0,0.1);
        }
        
        /* WhatsApp-style message pointers */
        .sender-message:after {
            content: "";
            position: absolute;
            right: -8px;
            top: 0;
            width: 0;
            height: 0;
            border: 8px solid transparent;
            border-left-color: #d9d9d9;
            border-right: 0;
        }
        
        .sender-message:before {
            content: "";
            position: absolute;
            right: -7px;
            top: 0;
            width: 0;
            height: 0;
            border: 7px solid transparent;
            border-left-color: white;
            border-right: 0;
            margin-top: 1px;
        }
        
        .receiver-message:after {
            content: "";
            position: absolute;
            left: -8px;
            top: 0;
            width: 0;
            height: 0;
            border: 8px solid transparent;
            border-right-color: #d9d9d9;
            border-left: 0;
        }
        
        .receiver-message:before {
            content: "";
            position: absolute;
            left: -7px;
            top: 0;
            width: 0;
            height: 0;
            border: 7px solid transparent;
            border-right-color: white;
            border-left: 0;
            margin-top: 1px;
        }
        
        /* Timestamp styling */
        .message-timestamp {
            font-size: 0.7em;
            color: #666;
            display: inline-block;
            float: right;
            margin-left: 8px;
            margin-top: 2px;
            vertical-align: bottom;
        }
        
        /* Date separator styling */
        .date-separator {
            text-align: center;
            margin: 15px 0;
            position: relative;
        }
        
        .date-separator span {
            background-color: #f0f0f0;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            color: #666;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if 'current_chat' not in st.session_state:
        st.session_state.current_chat = None
    
    # Get all conversations
    conversations = call_api(f"conversations/{st.session_state.user['id']}")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Conversations")
        if conversations:
            for conv in conversations:
                unread = "🔴" if conv.get('unread_count', 0) > 0 else ""
                if st.button(f"{unread} {conv.get('partner_name', 'Unknown')}", key=f"conv_{conv.get('partner_id', 0)}"):
                    st.session_state.current_chat = {
                        'receiver_id': conv.get('partner_id'),
                        'receiver_name': conv.get('partner_name', 'Unknown')
                    }
                    st.rerun()
        else:
            st.info("No conversations yet")
    
    with col2:
        if st.session_state.current_chat:
            st.subheader(f"Chat with {st.session_state.current_chat.get('receiver_name', 'Unknown')}")
            
            # Get message history
            messages = call_api(f"messages/{st.session_state.user['id']}/{st.session_state.current_chat['receiver_id']}")
            
            # Display messages with proper date grouping
            if messages:
                current_date = None
                for msg in messages:
                    # Parse timestamp
                    timestamp = msg.get('created_at', '')
                    try:
                        if timestamp:
                            if 'T' in timestamp:
                                date_part, time_part = timestamp.split('T')
                                time_part = time_part[:5]  # Get HH:MM
                            else:
                                date_part = timestamp[:10]
                                time_part = timestamp[11:16] if len(timestamp) > 16 else ''
                            
                            # Convert date to DD-MM-YYYY format
                            try:
                                date_obj = datetime.strptime(date_part, '%Y-%m-%d')
                                formatted_date = date_obj.strftime('%d-%m-%Y')
                            except:
                                formatted_date = date_part
                    except:
                        formatted_date = ''
                        time_part = ''
                    
                    # Show date separator if date changed
                    if formatted_date != current_date:
                        current_date = formatted_date
                        st.markdown(
                            f"""<div class="date-separator"><span>{formatted_date}</span></div>""",
                            unsafe_allow_html=True
                        )
                    
                    # Display message with timestamp
                    if msg.get('sender_id') == st.session_state.user['id']:
                        st.markdown(
                            f"""
                            <div class="message-container">
                                <div class="sender-message">
                                    {msg.get('content', '')}
                                    <span class="message-timestamp">{time_part}</span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div class="message-container">
                                <div class="receiver-message">
                                    {msg.get('content', '')}
                                    <span class="message-timestamp">{time_part}</span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.info("No messages in this conversation yet")
            
            # Send new message
            new_msg = st.chat_input("Type your message...")
            if new_msg:
                response = call_api("messages", "POST", {
                    "sender_id": st.session_state.user['id'],
                    "receiver_id": st.session_state.current_chat['receiver_id'],
                    "content": new_msg
                })
                if response and response.get('success'):
                    st.rerun()
        else:
            st.info("Select a conversation or start a new one")

        if st.session_state.current_chat and 'request_id' in st.session_state.current_chat:
        # Optional: Scroll to or highlight messages related to this request
            st.markdown(
                f"""<script>document.querySelector('[data-request-id="{st.session_state.current_chat['request_id']}"]')
                    .scrollIntoView({{behavior: 'smooth'}});</script>""",
                unsafe_allow_html=True
            )

# ----- Profile Page -----
def profile_tab():
    st.title("👤 My Profile")
    
    # Get current user data
    user_data = st.session_state.user
    if not user_data:
        st.error("User data not available")
        return
    
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Display current profile picture
            if user_data.get('profile_pic'):
                try:
                    st.image(
                        Image.open(BytesIO(base64.b64decode(user_data['profile_pic']))),
                        width=150,
                        caption="Your Profile Picture"
                    )
                except:
                    st.image(
                        "https://via.placeholder.com/150",
                        width=150,
                        caption="Default Profile Picture"
                    )
            else:
                st.image(
                    "https://via.placeholder.com/150",
                    width=150,
                    caption="Default Profile Picture"
                )
            
            # Upload new profile picture
            uploaded_file = st.file_uploader(
                "Upload new profile picture",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=False,
                key="profile_pic_uploader"
            )
            
            if uploaded_file:
                with st.spinner("Updating profile picture..."):
                    if handle_profile_pic_upload(uploaded_file, user_data['id']):
                        st.rerun()
        
        with col2:
            # Display user information
            st.subheader(user_data.get('name', 'User'))
            st.caption(f"Role: {st.session_state.role}")
            st.write(f"📍 {user_data.get('location', 'Not specified')}")
            st.write(f"📞 {user_data.get('phone', 'Not provided')}")
            st.write(f"✉️ {user_data.get('email', '')}")
    
    # Edit profile section
    with st.expander("Edit Profile Information"):
        with st.form("profile_form"):
            new_name = st.text_input("Name", value=user_data.get('name', ''))
            new_location = st.text_input("Location", value=user_data.get('location', ''))
            new_phone = st.text_input("Phone Number", value=user_data.get('phone', ''))
            
            if st.form_submit_button("Update Profile"):
                update_data = {
                    "user_id": user_data['id'],
                    "name": new_name,
                    "location": new_location,
                    "phone": new_phone
                }
                response = call_api("update_profile", "PUT", update_data)
                if response and response.get("success"):
                    st.session_state.user = response["user"]
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile")
    
    # Additional sections based on role
    if st.session_state.role == "Farmer":
        st.subheader("Farm Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Listings", "12")
        with col2:
            st.metric("Completed Transactions", "24")
        with col3:
            st.metric("Rating", "4.8 ★")
    
    elif st.session_state.role == "Buyer":
        st.subheader("Purchase History")
        # Display buyer-specific stats
        
    elif st.session_state.role == "Food Bank":
        st.subheader("Distribution Stats")
        # Display food bank-specific stats

    # Account management
    with st.expander("Account Settings", expanded=False):
        if st.button("Change Password"):
            st.session_state.profile_action = "change_password"
            st.rerun()
        
        if st.button("Delete Account", type="primary"):
            st.session_state.profile_action = "delete_account"
            st.rerun()

    # Handle profile actions
    if 'profile_action' in st.session_state:
        if st.session_state.profile_action == "change_password":
            change_password_form()
        elif st.session_state.profile_action == "delete_account":
            delete_account_confirmation()

def handle_profile_pic_upload(uploaded_file, user_id):
    if uploaded_file is not None:
        try:
            # Validate image
            img = Image.open(uploaded_file)
            img.verify()  # Verify it's a valid image
            
            # Process image
            img = Image.open(uploaded_file)  # Reopen after verify
            buffered = BytesIO()
            
            # Convert to RGB if needed (for PNG transparency)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            # Resize to reasonable dimensions
            max_size = (500, 500)
            img.thumbnail(max_size)
            
            # Save as JPEG with 85% quality
            img.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Update profile picture
            response = call_api("update_profile_pic", "PUT", {
                "user_id": user_id,
                "profile_pic": img_str
            })
            
            if response and response.get("success"):
                st.session_state.user = response["user"]
                st.success("Profile picture updated successfully!")
                return True
            else:
                error = response.get("error", "Unknown error") if response else "No response from server"
                st.error(f"Failed to update profile picture: {error}")
        except Exception as e:
            st.error(f"Invalid image: {str(e)}")
    return False

def change_password_form():
    with st.form("change_password"):
        st.subheader("Change Password")
        current_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Update Password"):
            if new_pw != confirm_pw:
                st.error("Passwords don't match")
            else:
                response = call_api("change_password", "POST", {
                    "user_id": st.session_state.user['id'],
                    "current_password": current_pw,
                    "new_password": new_pw
                })
                if response and response.get("success"):
                    st.success("Password changed successfully!")
                    del st.session_state.profile_action
                    st.rerun()
                else:
                    st.error(response.get("message", "Password change failed"))

def delete_account_confirmation():
    st.warning("⚠️ This action cannot be undone!")
    if st.button("Confirm Delete My Account", type="primary"):
        response = call_api(f"users/{st.session_state.user['id']}", "DELETE")
        if response and response.get("success"):
            st.success("Account deleted successfully")
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.page = "login"
            st.rerun()
    if st.button("Cancel"):
        del st.session_state.profile_action
        st.rerun()

# ----- Authentication Pages -----
def login_page():
    st.title("Login to Food Donation Network")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Farmer", "Buyer", "Food Bank"])
        
        if st.form_submit_button("Login"):
            response = call_api("login", "POST", {
                "email": email,
                "password": password,
                "role": role
            })
            
            if response and response.get("success"):
                st.session_state.user = response["user"]
                st.session_state.role = role
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Login failed. Please check your credentials.")

    if st.button("Register"):
        st.session_state.page = "register"
        st.rerun()

def register_page():
    st.title("Register for Food Donation Network")
    
    with st.form("register_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["Farmer", "Buyer", "Food Bank"])
        location = st.text_input("Location")
        phone = st.text_input("Phone Number")
        
        if st.form_submit_button("Register"):
            if password != confirm_password:
                st.error("Passwords do not match")
            else:
                response = call_api("register", "POST", {
                    "name": name,
                    "email": email,
                    "password": password,
                    "role": role,
                    "location": location,
                    "phone": phone
                })
                
                if response and response.get("success"):
                    st.success("Registration successful! Please login.")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error("Registration failed. Please try again.")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ----- Role-Specific Pages -----
def farmer_dashboard():
    st.title(f"👨‍🌾 Farmer Dashboard - Welcome {st.session_state.user['name']}")
    
    tabs = st.tabs(["Yield Prediction", "Post Listing", "My Listings", "Requests", "Messages", "Profile"])

    with tabs[0]:  # Yield Prediction tab
        yield_prediction_tab()
    
    with tabs[1]:
        with st.form("post_listing", clear_on_submit=True):
            st.subheader("Post New Listing")
            produce_type = st.text_input("Produce Type")
            quantity = st.number_input("Quantity (kg)", min_value=1)
            price = st.number_input("Price per kg (optional)", min_value=0)
            description = st.text_area("Description")
            harvest_date = st.date_input("Harvest Date")
            best_before = st.date_input("Best Before Date")
            organic = st.checkbox("Organic")
            
            # Image upload with validation
            uploaded_files = st.file_uploader(
                "Upload Images (JPEG/PNG only)", 
                type=["jpg", "jpeg", "png"], 
                accept_multiple_files=True,
                key="image_uploader"
            )
            
            if st.form_submit_button("Post Listing"):
                image_data = []
                for uploaded_file in uploaded_files:
                    if uploaded_file is not None:
                        try:
                            # Open and verify the image
                            image = Image.open(uploaded_file)
                            image.verify()  # Verify it's a valid image
                            
                            # Convert to bytes
                            image = Image.open(uploaded_file)  # Need to reopen after verify
                            buffered = BytesIO()
                            
                            # Convert to RGB if needed (for PNG transparency)
                            if image.mode in ("RGBA", "P"):
                                image = image.convert("RGB")
                                
                            image.save(buffered, format="JPEG", quality=85)
                            image_data.append(base64.b64encode(buffered.getvalue()).decode('utf-8'))
                        except Exception as e:
                            st.error(f"Invalid image: {uploaded_file.name}. Error: {str(e)}")
                            continue
                
                response = call_api("listings", "POST", {
                    "farmer_id": st.session_state.user["id"],
                    "produce_type": produce_type,
                    "quantity": quantity,
                    "price": price,
                    "description": description,
                    "harvest_date": harvest_date.isoformat(),
                    "best_before": best_before.isoformat(),
                    "organic": organic,
                    "images": image_data
                })
                
                if response and response.get("success"):
                    st.success("Listing posted successfully!")
                else:
                    st.error("Failed to post listing")

    with tabs[2]:
        st.subheader("My Active Listings")
        listings = call_api(f"listings/farmer/{st.session_state.user['id']}")
        
        if listings:
            for listing in listings:
                with st.expander(f"{listing['produce_type']} - {listing['quantity']}kg"):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if listing.get('images') and len(listing['images']) > 0:
                            try:
                                # Handle both string and list formats
                                img_data = listing['images']
                                if isinstance(img_data, str):
                                    img_data = json.loads(img_data)
                                
                                if img_data and len(img_data) > 0:
                                    img_bytes = base64.b64decode(img_data[0].encode('utf-8'))
                                    
                                    # Create temporary file to ensure proper handling
                                    with BytesIO(img_bytes) as img_buffer:
                                        try:
                                            img = Image.open(img_buffer)
                                            st.image(img, width=150)
                                        except:
                                            st.warning("Couldn't display image (invalid format)")
                            except Exception as e:
                                st.warning(f"Image display error: {str(e)}")
                    with col2:
                        st.write(f"**Description:** {listing['description']}")
                        st.write(f"**Harvest Date:** {listing['harvest_date']}")
                        st.write(f"**Best Before:** {listing['best_before']}")
                        st.write(f"**Organic:** {'Yes' if listing['organic'] else 'No'}")
                        st.write(f"**Status:** {listing['status']}")
                        
                        if st.button(f"Delete {listing['produce_type']}", key=f"del_{listing['id']}"):
                            if call_api(f"listings/{listing['id']}", "DELETE"):
                                st.rerun()
        else:
            st.info("You have no active listings")

    with tabs[3]:  # Requests tab
        st.subheader("Requests for Your Produce")
        response = call_api(f"requests/farmer/{st.session_state.user['id']}")
        
        # Handle API response
        if response is None:
            st.error("Failed to load requests. Please try again later.")
            return
            
        requests = response if isinstance(response, list) else []
        
        if requests:
            for req in requests:
                # Ensure req has all required fields
                if not all(k in req for k in ['id', 'produce_type', 'quantity', 'status']):
                    continue
                
                status_color = {
                    "pending": "blue",
                    "approved": "green",
                    "rejected": "red",
                    "completed": "purple"
                }.get(req['status'], "gray")
                
                with st.expander(f"{req['produce_type']} - {req['quantity']}kg (Status: :{status_color}[{req['status']}])"):
                    st.write(f"**Requester:** {req.get('requester_name', 'Unknown')}")
                    st.write(f"**Quantity Requested:** {req['quantity']}kg")
                    st.write(f"**Date Requested:** {req.get('created_at', 'Unknown')}")

                    # Add message button for each request
                    requester_id = req.get('buyer_id') or req.get('foodbank_id')
                    requester_name = req.get('requester_name', 'Unknown')
                    
                    if requester_id:  # Only show button if we have a valid ID
                        if st.button(f"📩 Message {requester_name}", key=f"msg_req_{req['id']}"):
                            st.session_state.current_chat = {
                                'receiver_id': requester_id,
                                'receiver_name': requester_name,
                                'request_id': req['id']
                            }
                            st.session_state.active_tab = "Messages"
                            st.rerun()
                    else:
                        st.warning("Could not identify requester")

                    
                    if req['status'] == "pending":
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Approve {req['produce_type']}", key=f"app_{req['id']}"):
                                with st.spinner("Processing approval..."):
                                    response = call_api(
                                        f"requests/{req['id']}", 
                                        "PUT", 
                                        {
                                            "status": "approved",
                                            "quantity": req['quantity'],
                                            "listing_id": req['listing_id'],
                                            "farmer_id": st.session_state.user['id']  # Add this line
                                        }
                                    )

                                    if response is None:
                                        st.error("Failed to connect to server")
                                    elif response.get("success"):
                                        st.success("Request approved successfully!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        error_msg = response.get("error", "Unknown error occurred")
                                        st.error(f"Approval failed: {error_msg}")
                        
                        with col2:
                            if st.button(f"Reject {req['produce_type']}", key=f"rej_{req['id']}"):
                                with st.spinner("Processing rejection..."):
                                    response = call_api(
                                        f"requests/{req['id']}", 
                                        "PUT", 
                                        {
                                            "status": "rejected",
                                            "quantity": 0,
                                            "listing_id": req['listing_id'],
                                            "farmer_id": st.session_state.user['id']
                                        }
                                    )
                                    if response is None:
                                        st.error("Failed to connect to server")
                                    elif response.get("success"):
                                        st.success("Request rejected successfully!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        error_msg = response.get("error", "Unknown error occurred")
                                        st.error(f"Rejection failed: {error_msg}")
                    else:
                        st.write(f"**Resolution:** This request has been {req['status']}")
        else:
            st.info("You have no pending requests")

    with tabs[4]:  # Messages tab
        messages_tab()

    with tabs[5]:  # Profile tab
        profile_tab()

    # Other tabs would be implemented similarly...

def buyer_dashboard():
    st.title(f"🛒 Buyer Dashboard - Welcome {st.session_state.user['name']}")
    
    tabs = st.tabs(["Browse Listings", "My Requests", "Messages", "Profile"])

    # # Initialize active tab if not set
    # if 'active_tab' not in st.session_state:
    #     st.session_state.active_tab = tabs[0]
    
    # # Create tabs
    # selected_tab = st.radio(
    #     "Navigation",
    #     tabs,
    #     index=tabs.index(st.session_state.active_tab),
    #     format_func=lambda x: "",
    #     horizontal=True,
    #     label_visibility="collapsed"
    # )
    
    # # Update active tab
    # st.session_state.active_tab = selected_tab
    
    with tabs[0]:
        st.subheader("Available Produce")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            produce_filter = st.text_input("Filter by produce type")
        with col2:
            organic_filter = st.selectbox("Organic", ["All", "Yes", "No"])
        with col3:
            distance_filter = st.slider("Max distance (km)", 0, 100, 50)
        
        listings = call_api("listings/active")
        
        if listings:
            for listing in listings:
                if produce_filter and produce_filter.lower() not in listing['produce_type'].lower():
                    continue
                if organic_filter == "Yes" and not listing['organic']:
                    continue
                if organic_filter == "No" and listing['organic']:
                    continue
                
                with st.expander(f"{listing['produce_type']} - {float(listing['quantity'])}kg"):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if listing.get('images') and listing['images']:
                            try:
                                img_data = listing['images']
                                if isinstance(img_data, str):
                                    img_data = json.loads(img_data)
                                
                                if img_data and len(img_data) > 0:
                                    img_bytes = base64.b64decode(img_data[0])
                                    img = Image.open(BytesIO(img_bytes))
                                    st.image(img, width=150)
                            except Exception as e:
                                st.warning(f"Couldn't load image: {str(e)}")
                    
                    with col2:
                        st.write(f"**Farmer:** {listing['farmer_name']}")
                        st.write(f"**Location:** {listing['location']}")
                        price = float(listing['price'])
                        st.write(f"**Price:** {'Free' if price == 0 else f'Ksh. {price:.2f}/kg'}")
                        st.write(f"**Organic:** {'Yes' if listing['organic'] else 'No'}")

                        if float(listing['quantity']) > 0:
                            max_qty = float(listing['quantity'])
                            if max_qty > 0:
                                quantity = st.number_input(
                                    "Quantity (kg)",
                                    min_value=0.1,
                                    max_value=max_qty,
                                    value=min(1.0, max_qty),  # Now safe because max_qty > 0
                                    step=0.1,
                                    key=f"qty_{listing['id']}"
                                )
                            
                            # # Ensure quantity is float type
                            # max_qty = float(listing['quantity'])
                            # quantity = st.number_input(
                            #     "Quantity (kg)",
                            #     min_value=1.0,  # Changed to float
                            #     max_value=max_qty,
                            #     value=min(1.0, max_qty),  # Default value
                            #     step=0.1,
                            #     key=f"qty_{listing['id']}"
                            # )
                            
                            if st.button("Request", key=f"req_{listing['id']}"):
                                response = call_api("requests", "POST", {
                                    "listing_id": listing['id'],
                                    "buyer_id": st.session_state.user['id'],
                                    "quantity": float(quantity),  # Ensure float
                                    "status": "pending"
                                })
                                if response and response.get("success"):
                                    st.success("Request sent successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to send request")

                            # Add message button next to request button
                            if st.button(f"📩 Message Farmer", key=f"msg_{listing['id']}"):
                                st.session_state.current_chat = {
                                    'receiver_id': listing['farmer_id'],
                                    'receiver_name': listing['farmer_name'],
                                    'listing_id': listing['id']
                                }
                                st.session_state.page = "messages"
                                st.rerun()
                        else:
                            # Show out of stock message and disabled button
                            st.error("❌ Out of Stock")
                            st.button("Request", disabled=True, help="This item is no longer available")
                            
                            # Optional: Update listing status to inactive in backend
                            if listing['status'] != 'inactive':
                                call_api(f"listings/{listing['id']}/status", "PUT", {"status": "inactive"})

        else:
            st.info("No listings available")

    with tabs[1]:  # My Requests tab
        st.subheader("My Requests")
        requests = call_api(f"requests/buyer/{st.session_state.user['id']}")
        
        if requests:
            for req in requests:
                status_color = {
                    "pending": "blue",
                    "approved": "green",
                    "rejected": "red",
                    "completed": "purple"
                }.get(req['status'], "gray")
                
                with st.expander(f"{req['produce_type']} - {req['quantity']}kg (Status: :{status_color}[{req['status']}])"):
                    st.write(f"**Farmer:** {req['farmer_name']}")
                    st.write(f"**Quantity:** {req['quantity']}kg")
                    st.write(f"**Date Requested:** {req['created_at']}")
                    st.write(f"**Status:** :{status_color}[{req['status'].title()}]")
                    
                    if req['status'] == "approved":
                        if st.button("Mark as Completed", key=f"comp_{req['id']}"):
                            if call_api(f"requests/{req['id']}", "PUT", {"status": "completed"}):
                                st.rerun()

                    # Add message button for each request
                    if st.button(f"📩 Message Farmer", key=f"msg_req_{req['id']}"):
                        if req.get('farmer_id'):  # Check if farmer_id exists
                            st.session_state.current_chat = {
                                'receiver_id': req['farmer_id'],  # Use farmer_id from request
                                'receiver_name': req['farmer_name']
                            }
                            st.session_state.active_tab = "Messages"
                            st.rerun()
                        else:
                            st.error("Could not identify farmer for this request")

        else:
            st.info("You haven't made any requests yet")

    with tabs[2]:  # Messages tab
        messages_tab()

    with tabs[3]:  # Profile tab
        profile_tab()

    # Other tabs would be implemented similarly...

def foodbank_dashboard():
    st.title(f"🏥 Food Bank Dashboard - Welcome {st.session_state.user['name']}")
    
    tabs = st.tabs(["Browse Listings", "My Requests", "Distribution Log", "Messages", "Profile"])
    
    with tabs[0]:
        st.subheader("Available Donations")
        
        listings = call_api("listings/donations")
        
        if listings:
            for listing in listings:
                with st.expander(f"{listing['produce_type']} - {listing['quantity']}kg"):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if listing.get('images'):
                            try:
                                # Handle both string and list formats
                                img_data = listing['images']
                                if isinstance(img_data, str):
                                    img_data = json.loads(img_data)  # If stored as JSON string
                                
                                if img_data and len(img_data) > 0:
                                    img_bytes = base64.b64decode(img_data[0].encode('utf-8'))
                                    img = Image.open(BytesIO(img_bytes))
                                    st.image(img, width=150)
                            except Exception as e:
                                st.warning(f"Couldn't display image: {str(e)}")
                        else:
                            st.image("placeholder.jpg", width=150)

                    with col2:
                        st.write(f"**Farmer:** {listing['farmer_name']}")
                        st.write(f"**Location:** {listing['location']}")
                        st.write(f"**Available Quantity:** {listing['quantity']}kg")
                        st.write(f"**Harvest Date:** {listing['harvest_date']}")
                        st.write(f"**Best Before:** {listing['best_before']}")
                        
                        try:
                            max_qty = float(listing['quantity'])
                        except:
                            max_qty = 0.0

                        quantity = st.number_input(
                            "Quantity (kg)", 
                            min_value=0.1,  # float instead of int
                            max_value=max_qty,  # Explicit conversion
                            value=min(1.0, max_qty),  # Default value as float
                            step=0.1,  # Allows decimal inputs
                            key=f"qty_{listing['id']}"
                        )

                        if f"confirm_{listing['id']}" not in st.session_state:
                            st.session_state[f"confirm_{listing['id']}"] = False

                        # First button (Request Donation)
                        if st.button("Request Donation", key=f"req_{listing['id']}"):
                            st.session_state[f"confirm_{listing['id']}"] = True

                        # Second step (only shows after first button click)
                        if st.session_state[f"confirm_{listing['id']}"]:
                            purpose = st.text_area("Purpose of donation", key=f"purp_{listing['id']}")
                            
                            if st.button("Confirm Request", key=f"conf_{listing['id']}"):
                                response = call_api("requests", "POST", {
                                    "listing_id": listing['id'],
                                    "foodbank_id": st.session_state.user['id'],
                                    "quantity": quantity,
                                    "purpose": purpose,
                                    "status": "pending"
                                })
                                
                                if response and response.get("success"):
                                    st.success("Donation request sent successfully!")
                                    st.session_state[f"confirm_{listing['id']}"] = False  # Reset
                                    st.rerun()
                                else:
                                    st.error("Failed to send request")

                        # quantity = st.number_input(
                        #     "Quantity (kg)", 
                        #     min_value=0.1,  # float instead of int
                        #     max_value=max_qty,  # Explicit conversion
                        #     value=min(1.0, max_qty),  # Default value as float
                        #     step=0.1,  # Allows decimal inputs
                        #     key=f"qty_{listing['id']}"
                        # )
        
                        # if st.button("Request Donation", key=f"req_{listing['id']}"):
                        #     if quantity > max_qty:
                        #         st.error("Requested quantity exceeds available stock")
                        #     else:
                        #         purpose = st.text_area("Purpose of donation", key=f"purp_{listing['id']}")
                        #         if st.button("Confirm Request", key=f"conf_{listing['id']}"):
                        #             response = call_api("requests", "POST", {
                        #                 "listing_id": listing['id'],
                        #                 "foodbank_id": st.session_state.user['id'],
                        #                 "quantity": quantity,
                        #                 "purpose": purpose,
                        #                 "status": "pending"
                        #             })
                        #             if response and response.get("success"):
                        #                 st.success("Donation request sent successfully!")
                        #             else:
                        #                 st.error("Failed to send request")
        else:
            st.info("No donation listings available")

    with tabs[1]:  # My Requests tab
        st.subheader("My Donation Requests")
        requests = call_api(f"requests/foodbank/{st.session_state.user['id']}")
        
        if requests:
            for req in requests:
                status_color = {
                    "pending": "blue",
                    "approved": "green",
                    "rejected": "red",
                    "completed": "purple"
                }.get(req['status'], "gray")
                
                with st.expander(f"{req['produce_type']} - {req['quantity']}kg (Status: :{status_color}[{req['status']}])"):
                    st.write(f"**Farmer:** {req['farmer_name']}")
                    st.write(f"**Quantity:** {req['quantity']}kg")
                    if req.get('purpose'):
                        st.write(f"**Purpose:** {req['purpose']}")
                    st.write(f"**Date Requested:** {req['created_at']}")
                    st.write(f"**Status:** :{status_color}[{req['status'].title()}]")
                    
                    if req['status'] == "approved":
                        if st.button("Mark as Received", key=f"recv_{req['id']}"):
                            if call_api(f"requests/{req['id']}", "PUT", {"status": "completed"}):
                                st.rerun()
        else:
            st.info("You haven't made any donation requests yet")
    
    with tabs[2]:  # Distribution Log tab
        st.subheader("Distribution Log")
        completed_requests = call_api(f"requests/foodbank/{st.session_state.user['id']}?status=completed")
        
        if completed_requests:
            distribution_data = []
            for req in completed_requests:
                distribution_data.append({
                    "Date": req['created_at'].split('T')[0],
                    "Produce": req['produce_type'],
                    "Quantity (kg)": req['quantity'],
                    "From": req['farmer_name'],
                    "Purpose": req.get('purpose', '')
                })
            
            df = pd.DataFrame(distribution_data)
            st.dataframe(df)
            
            # Export button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Export as CSV",
                csv,
                "food_distribution_log.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("No distribution records yet")

    with tabs[3]:  # Messages tab
        messages_tab()

    with tabs[4]:  # Profile tab
        profile_tab()

    # Other tabs would be implemented similarly...

# ----- Main App Flow -----
def main():
    st.sidebar.title("Food Donation Network")
    
    if st.session_state.user:
        st.sidebar.write(f"Logged in as: {st.session_state.user['name']}")
        st.sidebar.write(f"Role: {st.session_state.role}")
        
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.page = "login"
            st.rerun()
        
        if st.session_state.role == "Farmer":
            farmer_dashboard()
        elif st.session_state.role == "Buyer":
            buyer_dashboard()
        elif st.session_state.role == "Food Bank":
            foodbank_dashboard()
    else:
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "register":
            register_page()

if __name__ == "__main__":
    main()
