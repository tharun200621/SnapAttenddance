import streamlit as st


def style_background_home():
    st.markdown("""
        <style>
            .stApp {
                background: #5865F2 !important;
            }
            .stApp div[data-testid="stColumn"] {
    background-color: #E0E3FF !important;
    padding: 2.5rem !important;
    border-radius: 5rem !important;
}    
        </style>
    """, unsafe_allow_html=True)

def style_background_dashboard():
    st.markdown("""
        <style>

            .stApp {
                background: linear-gradient(
                    rgba(255,255,255,0.92),
                    rgba(255,255,255,0.92)
                ),
                url("https://images.unsplash.com/photo-1522202176988-66273c2fd55f");
                
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }

            /* Main content cards */
            div[data-testid="stVerticalBlock"] > div {
                border-radius: 25px;
            }

            /* Headers visibility */
            h1 {
                color: black !important;
            }

            h2 {
                color: black !important;
            }

            h3, h4, h5, h6, p, label, span {
                color: #1e293b !important;
            }

            /* Input fields */
            .stTextInput input {
                background-color: white !important;
                color: black !important;
                border: 2px solid #dbe2ff !important;
                border-radius: 15px !important;
                padding: 10px !important;
            }

            /* Camera input area */
            section[data-testid="stFileUploader"] {
                background-color: rgba(255,255,255,0.75);
                border-radius: 20px;
                padding: 20px;
            }

            /* Audio recorder area */
            div[data-testid="stAudioInput"] {
                background-color: rgba(255,255,255,0.75);
                border-radius: 20px;
                padding: 15px;
            }

            /* Container cards */
            div[data-testid="stContainer"] {
                background-color: rgba(255,255,255,0.65);
                backdrop-filter: blur(10px);
                border-radius: 25px;
                padding: 20px;
            }

            /* Better button hover */
            .stButton button:hover {
                transform: scale(1.03);
                transition: 0.2s ease;
            }

        </style>
    """, unsafe_allow_html=True)

def style_base_layout():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');

            /* Hide Top Bar of streamlit */
            #MainMenu, footer, header {
                visibility: hidden;
            }

            .block-container {
                padding-top: 1.5rem !important;
            }

            h1 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 3.5rem !important;
                line-height: 1.1 !important;
                margin-bottom: 0rem !important;
            }

            h2 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 2 rem !important;
                line-height: 1.1 !important;
                margin-bottom: 0rem !important;
                color:black !important;
            }

            h3, h4, p {
                font-family: 'Outfit', sans-serif;
            }

            button {
                border-radius: 1.5rem !important;
                background: #5865F2 !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
            }

            button[kind="secondary"] {
                border-radius: 1.5rem !important;
                background: #EB459E !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
            }

            button[kind="tertiary"] {
                border-radius: 1.5rem !important;
                background: black !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
            }
        </style>
    """, unsafe_allow_html=True)