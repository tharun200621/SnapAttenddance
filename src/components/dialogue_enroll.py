import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

import time


@st.dialog("Enroll in Subject")
def enroll_dialogue():

    st.write(
        'Enter the subject code provided '
        'by your teacher to enroll'
    )

    join_code = st.text_input(
        'Subject Code',
        placeholder='Eg. CS101'
    )

    if st.button(
        'Enroll now',
        type='primary',
        width='stretch'
    ):

        # =================================================
        # VALIDATION
        # =================================================

        if not join_code:

            st.warning(
                'Please enter a subject code'
            )

            return

        # =================================================
        # CLEAN INPUT
        # =================================================

        join_code = join_code.strip().upper()

        # =================================================
        # FIND SUBJECT
        # =================================================

        res = (
            supabase
            .table('subjects')
            .select(
                'subject_id, name, subject_code'
            )
            .eq(
                'subject_code',
                join_code
            )
            .execute()
        )

        # =================================================
        # SUBJECT FOUND
        # =================================================

        if res.data:

            subject = res.data[0]

            student_id = (
                st.session_state
                .student_data['student_id']
            )

            # =============================================
            # CHECK ALREADY ENROLLED
            # =============================================

            check = (
                supabase
                .table('subject_student')
                .select('*')
                .eq(
                    'subject_id',
                    subject['subject_id']
                )
                .eq(
                    'student_id',
                    student_id
                )
                .execute()
            )

            # =============================================
            # ALREADY ENROLLED
            # =============================================

            if check.data:

                st.warning(
                    'You are already enrolled '
                    'in this course'
                )

            # =============================================
            # ENROLL STUDENT
            # =============================================

            else:

                enroll_student_to_subject(
                    student_id,
                    subject['subject_id']
                )

                st.success(
                    'Successfully enrolled!'
                )

                time.sleep(1)

                st.rerun()

        # =================================================
        # INVALID SUBJECT CODE
        # =================================================

        else:

            st.error(
                'Invalid subject code!'
            )