# app.py - PisoUno Coin Detection System
# Simplified version using only PIL (no OpenCV or sklearn required)

import streamlit as st
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
import tempfile
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="PisoUno - 1 Peso Coin Detection",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .coin-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .total-value-text {
        font-size: 2rem;
        font-weight: bold;
        color: #2e7d32;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>PisoUno</h1>
    <p>Old and New 1 Peso Coin Detection System</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'old_count' not in st.session_state:
    st.session_state.old_count = 0
    st.session_state.new_count = 0
    st.session_state.total_value = 0
    st.session_state.processed = False

# Sidebar for manual counting
with st.sidebar:
    st.header("Coin Counter")
    
    st.subheader("Manual Counting")
    st.info("Since the system is having issues with package installations, use this manual counter for now.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+ Old Coin", use_container_width=True):
            st.session_state.old_count += 1
            st.session_state.total_value = st.session_state.old_count + st.session_state.new_count
            st.session_state.processed = True
    
    with col2:
        if st.button("+ New Coin", use_container_width=True):
            st.session_state.new_count += 1
            st.session_state.total_value = st.session_state.old_count + st.session_state.new_count
            st.session_state.processed = True
    
    if st.button("Reset Counter", use_container_width=True):
        st.session_state.old_count = 0
        st.session_state.new_count = 0
        st.session_state.total_value = 0
        st.session_state.processed = True
        st.rerun()

# Main area
st.header("Coin Detection and Counting")

# Display current counts
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="coin-card">
        <div>OLD COINS</div>
        <div style="font-size: 2rem; font-weight: bold; color: #8B4513;">{st.session_state.old_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="coin-card">
        <div>NEW COINS</div>
        <div style="font-size: 2rem; font-weight: bold; color: #4169E1;">{st.session_state.new_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="coin-card">
        <div>TOTAL VALUE</div>
        <div class="total-value-text">PHP {st.session_state.total_value}.00</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Image upload for coin detection (using simple image features)
st.subheader("Coin Image Analysis")

uploaded_file = st.file_uploader("Upload coin image for analysis", type=['jpg', 'jpeg', 'png'])

def analyze_coin_image(image):
    """Analyze coin image using basic image processing"""
    # Convert to numpy array
    img_array = np.array(image)
    
    # Calculate average brightness
    brightness = np.mean(img_array)
    
    # Calculate color distribution
    if len(img_array.shape) == 3:
        r_avg = np.mean(img_array[:,:,0])
        g_avg = np.mean(img_array[:,:,1])
        b_avg = np.mean(img_array[:,:,2])
    else:
        r_avg = g_avg = b_avg = brightness
    
    # Calculate contrast (standard deviation)
    contrast = np.std(img_array)
    
    # Simple classification based on color and brightness
    # Old coins tend to be darker/brownish, new coins are brighter/silver
    if brightness < 100:
        suggestion = "OLD (darker appearance)"
        confidence = 0.7
    elif brightness > 150:
        suggestion = "NEW (brighter appearance)"
        confidence = 0.7
    else:
        # Check color balance
        if r_avg > g_avg and r_avg > b_avg:
            suggestion = "OLD (warm/brown tone)"
            confidence = 0.6
        else:
            suggestion = "NEW (cool/silver tone)"
            confidence = 0.6
    
    return suggestion, confidence, brightness, contrast

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption="Uploaded Coin Image", use_container_width=True)
    
    # Analyze the image
    with st.spinner("Analyzing coin image..."):
        suggestion, confidence, brightness, contrast = analyze_coin_image(image)
    
    with col2:
        st.subheader("Analysis Result")
        st.write(f"**Detection suggests:** {suggestion}")
        st.write(f"**Confidence:** {confidence:.1%}")
        st.write(f"**Image Brightness:** {brightness:.1f}")
        st.write(f"**Image Contrast:** {contrast:.1f}")
        
        st.info("Note: This is a simplified analysis. For best results, use the manual counter.")
        
        # Option to add based on suggestion
        if st.button("Add as suggested"):
            if "OLD" in suggestion:
                st.session_state.old_count += 1
            else:
                st.session_state.new_count += 1
            st.session_state.total_value = st.session_state.old_count + st.session_state.new_count
            st.success(f"Added as {suggestion}")
            st.rerun()

# Instructions
st.markdown("---")
with st.expander("How to use this system"):
    st.markdown("""
    **Current Mode: Manual Counter**
    
    Due to technical limitations with package installations on Streamlit Cloud, the system is currently running in manual mode.
    
    **How to use:**
    1. Use the sidebar buttons to count OLD and NEW coins
    2. The total value is automatically calculated (PHP 1.00 per coin)
    3. Use the Reset button to clear all counts
    
    **Image Analysis (Limited):**
    - You can upload coin images for basic analysis
    - The system will suggest whether it's OLD or NEW based on color and brightness
    - This is a simplified analysis and may not be 100% accurate
    
    **Full System Features (When packages are properly installed):**
    - Automatic coin detection using Hough Circle detection
    - SVM classifier for OLD vs NEW classification
    - Multiple coin detection in one image
    - Feature extraction using Hu moments and HOG
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p><strong>PisoUno</strong> - Philippine 1 Peso Coin Detection System</p>
    <p>Current Mode: Manual Counter | Full ML features pending package installation</p>
</div>
""", unsafe_allow_html=True)# app.py - PisoUno Coin Detection System
# Simplified version using only PIL (no OpenCV or sklearn required)

import streamlit as st
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
import tempfile
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="PisoUno - 1 Peso Coin Detection",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .coin-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .total-value-text {
        font-size: 2rem;
        font-weight: bold;
        color: #2e7d32;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>PisoUno</h1>
    <p>Old and New 1 Peso Coin Detection System</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'old_count' not in st.session_state:
    st.session_state.old_count = 0
    st.session_state.new_count = 0
    st.session_state.total_value = 0
    st.session_state.processed = False

# Sidebar for manual counting
with st.sidebar:
    st.header("Coin Counter")
    
    st.subheader("Manual Counting")
    st.info("Since the system is having issues with package installations, use this manual counter for now.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+ Old Coin", use_container_width=True):
            st.session_state.old_count += 1
            st.session_state.total_value = st.session_state.old_count + st.session_state.new_count
            st.session_state.processed = True
    
    with col2:
        if st.button("+ New Coin", use_container_width=True):
            st.session_state.new_count += 1
            st.session_state.total_value = st.session_state.old_count + st.session_state.new_count
            st.session_state.processed = True
    
    if st.button("Reset Counter", use_container_width=True):
        st.session_state.old_count = 0
        st.session_state.new_count = 0
        st.session_state.total_value = 0
        st.session_state.processed = True
        st.rerun()

# Main area
st.header("Coin Detection and Counting")

# Display current counts
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="coin-card">
        <div>OLD COINS</div>
        <div style="font-size: 2rem; font-weight: bold; color: #8B4513;">{st.session_state.old_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="coin-card">
        <div>NEW COINS</div>
        <div style="font-size: 2rem; font-weight: bold; color: #4169E1;">{st.session_state.new_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="coin-card">
        <div>TOTAL VALUE</div>
        <div class="total-value-text">PHP {st.session_state.total_value}.00</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Image upload for coin detection (using simple image features)
st.subheader("Coin Image Analysis")

uploaded_file = st.file_uploader("Upload coin image for analysis", type=['jpg', 'jpeg', 'png'])

def analyze_coin_image(image):
    """Analyze coin image using basic image processing"""
    # Convert to numpy array
    img_array = np.array(image)
    
    # Calculate average brightness
    brightness = np.mean(img_array)
    
    # Calculate color distribution
    if len(img_array.shape) == 3:
        r_avg = np.mean(img_array[:,:,0])
        g_avg = np.mean(img_array[:,:,1])
        b_avg = np.mean(img_array[:,:,2])
    else:
        r_avg = g_avg = b_avg = brightness
    
    # Calculate contrast (standard deviation)
    contrast = np.std(img_array)
    
    # Simple classification based on color and brightness
    # Old coins tend to be darker/brownish, new coins are brighter/silver
    if brightness < 100:
        suggestion = "OLD (darker appearance)"
        confidence = 0.7
    elif brightness > 150:
        suggestion = "NEW (brighter appearance)"
        confidence = 0.7
    else:
        # Check color balance
        if r_avg > g_avg and r_avg > b_avg:
            suggestion = "OLD (warm/brown tone)"
            confidence = 0.6
        else:
            suggestion = "NEW (cool/silver tone)"
            confidence = 0.6
    
    return suggestion, confidence, brightness, contrast

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption="Uploaded Coin Image", use_container_width=True)
    
    # Analyze the image
    with st.spinner("Analyzing coin image..."):
        suggestion, confidence, brightness, contrast = analyze_coin_image(image)
    
    with col2:
        st.subheader("Analysis Result")
        st.write(f"**Detection suggests:** {suggestion}")
        st.write(f"**Confidence:** {confidence:.1%}")
        st.write(f"**Image Brightness:** {brightness:.1f}")
        st.write(f"**Image Contrast:** {contrast:.1f}")
        
        st.info("Note: This is a simplified analysis. For best results, use the manual counter.")
        
        # Option to add based on suggestion
        if st.button("Add as suggested"):
            if "OLD" in suggestion:
                st.session_state.old_count += 1
            else:
                st.session_state.new_count += 1
            st.session_state.total_value = st.session_state.old_count + st.session_state.new_count
            st.success(f"Added as {suggestion}")
            st.rerun()

# Instructions
st.markdown("---")
with st.expander("How to use this system"):
    st.markdown("""
    **Current Mode: Manual Counter**
    
    Due to technical limitations with package installations on Streamlit Cloud, the system is currently running in manual mode.
    
    **How to use:**
    1. Use the sidebar buttons to count OLD and NEW coins
    2. The total value is automatically calculated (PHP 1.00 per coin)
    3. Use the Reset button to clear all counts
    
    **Image Analysis (Limited):**
    - You can upload coin images for basic analysis
    - The system will suggest whether it's OLD or NEW based on color and brightness
    - This is a simplified analysis and may not be 100% accurate
    
    **Full System Features (When packages are properly installed):**
    - Automatic coin detection using Hough Circle detection
    - SVM classifier for OLD vs NEW classification
    - Multiple coin detection in one image
    - Feature extraction using Hu moments and HOG
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p><strong>PisoUno</strong> - Philippine 1 Peso Coin Detection System</p>
    <p>Current Mode: Manual Counter | Full ML features pending package installation</p>
</div>
""", unsafe_allow_html=True)
