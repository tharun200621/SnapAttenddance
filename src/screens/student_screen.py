import streamlit as st
import numpy as np
from PIL import Image
import cv2
import time

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout
)

from src.components.header import (
    header_dashboard
)

from src.components.dialogue_enroll import (
    enroll_dialogue
)

from src.components.subject_card import (
    subject_card
)

from src.pipeline.face_pipeline import (
    predict_attendance,
    get_face_embeddings
)

from src.pipeline.voice_pipeline import (
    get_voice_embedding
)

from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject
)


# =========================================================
# IMAGE ENHANCEMENT
# =========================================================

def enhance_image(image_np):

    if image_np.shape[2] == 4:

        image_np = cv2.cvtColor(
            image_np,
            cv2.COLOR_RGBA2RGB
        )

    lab = cv2.cvtColor(
        image_np,
        cv2.COLOR_RGB2LAB
    )

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )

    l = clahe.apply(l)

    lab = cv2.merge((l, a, b))

    return cv2.cvtColor(
        lab,
        cv2.COLOR_LAB2RGB
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

def student_dashboard():

    student_data = st.session_state.student_data

    student_id = student_data['student_id']

    # =====================================================
    # HEADER
    # =====================================================

    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap='xxlarge'
    )

    with c1:

        header_dashboard()

    with c2:

        st.subheader(
            f"""Welcome, {student_data['name']} 👋"""
        )

        if st.button(
            "Logout",
            type='secondary',
            key='logoutbtn'
        ):

            st.query_params.clear()

            st.session_state.clear()

            st.rerun()

    st.space()

    # =====================================================
    # SUBJECT HEADER
    # =====================================================

    c1, c2 = st.columns(2)

    with c1:

        st.header('Your Enrolled Subjects')

    with c2:

        if st.button(
            'Enroll in Subject',
            type='primary',
            width='stretch'
        ):

            enroll_dialogue()

    st.divider()

    # =====================================================
    # LOAD SUBJECTS
    # =====================================================

    with st.spinner(
        'Loading your enrolled subjects...'
    ):

        subjects = get_student_subjects(
            student_id
        )

        logs = get_student_attendance(
            student_id
        )

    # =====================================================
    # ATTENDANCE STATS
    # =====================================================

    stats_map = {}

    for log in logs:

        sid = log['subject_id']

        if sid not in stats_map:

            stats_map[sid] = {
                "total": 0,
                "attended": 0
            }

        stats_map[sid]['total'] += 1

        if log.get('is_present'):

            stats_map[sid]['attended'] += 1

    # =====================================================
    # SUBJECT CARDS
    # =====================================================

    cols = st.columns(2)

    for i, sub_node in enumerate(subjects):

        sub = sub_node['subjects']

        sid = sub['subject_id']

        stats = stats_map.get(
            sid,
            {
                "total": 0,
                "attended": 0
            }
        )

        # =================================================
        # UNENROLL BUTTON
        # =================================================

        def unenroll_button():

            if st.button(
                "Unenroll from this course",
                type='tertiary',
                width='stretch',
                icon=':material/delete_forever:',
                key=f'unenroll_{sid}'
            ):

                unenroll_student_to_subject(
                    student_id,
                    sid
                )

                st.toast(
                    f'Unenrolled from {sub["name"]} successfully!'
                )

                st.rerun()

        # =================================================
        # SUBJECT CARD
        # =================================================

        with cols[i % 2]:

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],

                stats=[
                    (
                        '📆',
                        'Total',
                        stats['total']
                    ),

                    (
                        '✅',
                        'Attended',
                        stats['attended']
                    ),
                ],

                footer_callback=unenroll_button
            )


# =========================================================
# STUDENT SCREEN
# =========================================================

def student_screen():

    style_base_layout()

    style_background_dashboard()

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if (
        st.session_state.get("is_logged_in")
        and st.session_state.get("user_role")
        == "student"
        and st.session_state.get(
            "student_data"
        )
    ):

        student_dashboard()

        return

    # =====================================================
    # HEADER
    # =====================================================

    c1, c2 = st.columns(
        [3, 1],
        vertical_alignment='center'
    )

    with c1:

        header_dashboard()

    with c2:

        if st.button(
            "Go back to Home",
            type='secondary',
            key='homebtn'
        ):

            st.session_state[
                'login_type'
            ] = None

            st.session_state[
                'show_registration'
            ] = False

            st.rerun()

    # =====================================================
    # TITLE
    # =====================================================

    st.header(
        "Login using Face ID",
        text_alignment='center'
    )

    st.space()
    st.space()

    # =====================================================
    # SESSION STATE
    # =====================================================

    if (
        'show_registration'
        not in st.session_state
    ):

        st.session_state[
            'show_registration'
        ] = False

    # =====================================================
    # CAMERA INPUT
    # =====================================================

    photo_source = st.camera_input(
        "Please place your face at the center"
    )

    # =====================================================
    # FACE LOGIN
    # =====================================================

    if photo_source:

        img = Image.open(
            photo_source
        ).convert("RGB")

        img = np.array(img)

        with st.spinner(
            'AI is scanning...'
        ):

            detected, all_ids, num_faces = (
                predict_attendance(img)
            )

        # =================================================
        # NO FACE
        # =================================================

        if num_faces == 0:

            st.error(
                '❌ Face not found!'
            )

            st.info(
                'Try improving lighting and face position.'
            )

        # =================================================
        # MULTIPLE FACES
        # =================================================

        elif num_faces > 1:

            st.error(
                '❌ Multiple faces detected!'
            )

        # =================================================
        # FACE FOUND
        # =================================================

        else:

            if detected:

                student_id = list(
                    detected.keys()
                )[0]

                all_students = (
                    get_all_students()
                )

                student = next(
                    (
                        s for s in all_students
                        if str(
                            s['student_id']
                        )
                        == str(student_id)
                    ),
                    None
                )

                # =========================================
                # LOGIN SUCCESS
                # =========================================

                if student:

                    st.session_state[
                        'is_logged_in'
                    ] = True

                    st.session_state[
                        'user_role'
                    ] = 'student'

                    st.session_state[
                        'student_data'
                    ] = student

                    st.session_state[
                        'show_registration'
                    ] = False

                    st.success(
                        f"Welcome Back "
                        f"{student['name']} 👋"
                    )

                    time.sleep(1)

                    st.rerun()

                else:

                    st.warning(
                        'Profile not found.'
                    )

                    st.session_state[
                        'show_registration'
                    ] = True

            # =============================================
            # FACE NOT RECOGNIZED
            # =============================================

            else:

                st.info(
                    'Face not recognized! '
                    'Please register.'
                )

                st.session_state[
                    'show_registration'
                ] = True

    # =====================================================
    # REGISTRATION
    # =====================================================

    if st.session_state[
        'show_registration'
    ]:

        with st.container(border=True):

            st.header(
                'Register New Profile'
            )

            new_name = st.text_input(
                "Enter your name",
                placeholder='E.g. Hamza Rizvi'
            )

            st.subheader(
                'Optional : Voice Enrollment'
            )

            st.info(
                "Enroll your voice for "
                "voice attendance"
            )

            audio_data = None

            try:

                audio_data = st.audio_input(
                    'Record a short phrase'
                )

            except Exception:

                st.error(
                    'Audio recording failed!'
                )

            # =================================================
            # CREATE ACCOUNT
            # =================================================

            if st.button(
                'Create Account',
                type='primary'
            ):

                if new_name:

                    if not photo_source:

                        st.warning(
                            'Please capture your face first.'
                        )

                    else:

                        with st.spinner(
                            'Creating profile...'
                        ):

                            img = Image.open(
                                photo_source
                            ).convert("RGB")

                            img = np.array(img)

                            encodings = (
                                get_face_embeddings(img)
                            )

                        if encodings:

                            face_emb = (
                                encodings[0].tolist()
                            )

                            voice_emb = None

                            if audio_data:

                                voice_emb = (
                                    get_voice_embedding(
                                        audio_data.read()
                                    )
                                )

                            response_data = (
                                create_student(
                                    new_name,
                                    face_embedding=face_emb,
                                    voice_embedding=voice_emb
                                )
                            )

                            if response_data:

                                st.cache_resource.clear()

                                st.cache_data.clear()

                                st.session_state[
                                    'is_logged_in'
                                ] = True

                                st.session_state[
                                    'user_role'
                                ] = 'student'

                                st.session_state[
                                    'student_data'
                                ] = response_data[0]

                                st.session_state[
                                    'show_registration'
                                ] = False

                                st.success(
                                    f"Profile created! "
                                    f"Hi, {new_name} 👋"
                                )

                                time.sleep(1)

                                st.rerun()

                            else:

                                st.error(
                                    'Failed to create profile.'
                                )

                        else:

                            st.error(
                                'Could not detect face.'
                            )

                else:

                    st.warning(
                        'Please enter your name!'
                    )