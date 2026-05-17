import streamlit as st
import segno
import io


@st.dialog("Share Class Link")
def share_subject_dialogue(subject_name, subject_code):

    # CHANGE THIS TO YOUR DEPLOYED URL
    app_domain = "snapclass-main.streamlit.app"
    # Join URL
    join_url = f"{app_domain}/?join-code={subject_code}"

    st.header("Scan to Join")

    # Generate QR
    qr = segno.make(join_url)

    # Save QR to memory
    out = io.BytesIO()

    qr.save(
        out,
        kind='png',
        scale=10,
        border=1
    )

    # Layout
    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Copy Link")
        st.code(join_url, language="text")

        st.markdown("### Subject Code")
        st.code(subject_code, language="text")

        st.info("Copy this link or code to share on WhatsApp or Email")

    with col2:

        st.markdown("### Scan to Join")

        st.image(
            out.getvalue(),
            caption="QR Code for class joining"
        )