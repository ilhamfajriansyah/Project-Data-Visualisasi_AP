import streamlit as st
from PIL import Image
import os

# Page configuration
st.set_page_config(
    page_title="Monitoring Dashboard Pendapatan Tenant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide the sidebar and streamlit menu
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        #MainMenu { display: none; }
        .stDeployButton { display: none; }
        footer { display: none; }
        header { display: none; }
    </style>
""", unsafe_allow_html=True)

# Custom CSS for the login page
st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: white;
        }
        
        .main-container {
            display: flex;
            height: 100vh;
            width: 100%;
        }
        
        .left-section {
            flex: 1;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7aa8d1 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            position: relative;
            overflow: hidden;
        }
        
        .left-section::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: moveBackground 20s linear infinite;
        }
        
        @keyframes moveBackground {
            0% { transform: translate(0, 0); }
            100% { transform: translate(50px, 50px); }
        }
        
        .illustration-container {
            position: relative;
            z-index: 10;
            width: 100%;
            max-width: 500px;
            text-align: center;
        }
        
        .illustration-container img {
            width: 100%;
            height: auto;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .right-section {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f8f9fb;
            padding: 40px;
        }
        
        .login-card {
            width: 100%;
            max-width: 420px;
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }
        
        .logo-container {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo-container img {
            width: 60px;
            height: 60px;
            object-fit: contain;
        }
        
        .logo-text {
            font-size: 12px;
            color: #666;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .login-title {
            font-size: 24px;
            font-weight: 700;
            color: #1a1a1a;
            margin: 20px 0 8px 0;
            text-align: center;
        }
        
        .login-subtitle {
            font-size: 14px;
            color: #666;
            text-align: center;
            margin-bottom: 24px;
            line-height: 1.5;
        }
        
        .role-tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            border-bottom: 1px solid #e5e5e5;
        }
        
        .role-tab {
            flex: 1;
            padding: 12px 16px;
            border: none;
            background: transparent;
            color: #999;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
        }
        
        .role-tab.active {
            color: #2a5298;
            border-bottom-color: #2a5298;
        }
        
        .role-tab:hover {
            color: #2a5298;
        }
        
        .form-group {
            margin-bottom: 16px;
        }
        
        .form-label {
            font-size: 13px;
            font-weight: 500;
            color: #333;
            margin-bottom: 6px;
            display: block;
        }
        
        .form-input {
            width: 100%;
            padding: 12px 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.2s ease;
            background: #f9f9f9;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #2a5298;
            background: white;
            box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1);
        }
        
        .form-input::placeholder {
            color: #bbb;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            font-size: 13px;
        }
        
        .checkbox-wrapper {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .checkbox-wrapper input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: #2a5298;
        }
        
        .checkbox-wrapper label {
            cursor: pointer;
            color: #666;
            margin: 0;
        }
        
        .forgot-password {
            color: #2a5298;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease;
        }
        
        .forgot-password:hover {
            color: #1e3c72;
            text-decoration: underline;
        }
        
        .signin-button {
            width: 100%;
            padding: 12px 16px;
            background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .signin-button::before {
            content: '→';
            position: absolute;
            right: 16px;
            opacity: 0;
            transition: all 0.3s ease;
        }
        
        .signin-button:hover {
            box-shadow: 0 8px 24px rgba(42, 82, 152, 0.3);
            transform: translateY(-2px);
        }
        
        .signin-button:hover::before {
            opacity: 1;
            right: 12px;
        }
        
        .signin-button:active {
            transform: translateY(0);
        }
        
        @media (max-width: 1024px) {
            .left-section {
                display: none;
            }
            
            .right-section {
                flex: 1;
            }
        }
        
        @media (max-width: 768px) {
            .login-card {
                padding: 30px 20px;
            }
            
            .login-title {
                font-size: 20px;
            }
            
            .login-subtitle {
                font-size: 13px;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = 'user'

if 'remember_me' not in st.session_state:
    st.session_state.remember_me = False

# HTML structure for the login page
html_content = """
<div class="main-container">
    <!-- Left Section: Illustration -->
    <div class="left-section">
        <div class="illustration-container">
            <img src="airport_illustration.jpg" alt="Airport Dashboard">
        </div>
    </div>
    
    <!-- Right Section: Login Panel -->
    <div class="right-section">
        <div class="login-card">
            <!-- Logo -->
            <div class="logo-container">
                <img src="airport_logo.jpg" alt="Airport Company Logo">
                <div class="logo-text">Airport Company</div>
            </div>
            
            <!-- Title and Subtitle -->
            <h1 class="login-title">Monitoring Dashboard<br>Pendapatan Tenant</h1>
            <p class="login-subtitle">Please log in according to your access rights.</p>
            
            <!-- Role Selection Tabs -->
            <div class="role-tabs">
                <button class="role-tab active" data-role="user">User</button>
                <button class="role-tab" data-role="admin">Admin</button>
            </div>
            
            <!-- Login Form -->
            <form id="loginForm">
                <!-- Email Field -->
                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" class="form-input" placeholder="your.email@example.com" required>
                </div>
                
                <!-- Password Field -->
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-input" placeholder="••••••••" required>
                </div>
                
                <!-- Remember Me & Forgot Password -->
                <div class="checkbox-group">
                    <div class="checkbox-wrapper">
                        <input type="checkbox" id="rememberMe">
                        <label for="rememberMe">Remember me</label>
                    </div>
                    <a href="#" class="forgot-password">Forgot Password?</a>
                </div>
                
                <!-- Sign In Button -->
                <button type="submit" class="signin-button">Sign In</button>
            </form>
        </div>
    </div>
</div>

<script>
    // Role tab switching
    document.querySelectorAll('.role-tab').forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelectorAll('.role-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Form submission
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = this.querySelector('input[type="email"]').value;
        const password = this.querySelector('input[type="password"]').value;
        const rememberMe = document.getElementById('rememberMe').checked;
        
        console.log('Login attempt:', { email, rememberMe });
        alert('Login functionality would be implemented here.');
    });
</script>
"""

st.markdown(html_content, unsafe_allow_html=True)
