import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.components.dialogue_auto_enroll import (
    auto_enroll_dialogue
)


def main():
    st.set_page_config(
        page_title='SnapClass-Making attendance faster by AI',
        page_icon="https://i.ibb.co/YTYGn5qV/logo.png"
    )
    if 'login_type' not in st.session_state:

        st.session_state['login_type'] = None

    # =====================================================
    # JOIN CODE CHECK
    # =====================================================

    join_code = st.query_params.get('join-code')

    if join_code:

        if st.session_state.login_type != 'student':

            st.session_state.login_type = 'student'

            st.session_state['pending_join_code'] = join_code

            st.query_params.clear()

            st.rerun()

        elif 'pending_join_code' not in st.session_state:

            st.session_state['pending_join_code'] = join_code

            st.query_params.clear()

    # =====================================================
    # ROUTING
    # =====================================================

    match st.session_state['login_type']:

        case 'teacher':

            teacher_screen()

        case 'student':

            student_screen()

        case None:

            home_screen()

    # =====================================================
    # AUTO ENROLL
    # =====================================================

    pending_code = st.session_state.get('pending_join_code')

    if (
        pending_code
        and st.session_state.get('is_logged_in')
        and st.session_state.get('user_role') == 'student'
    ):

        auto_enroll_dialogue(pending_code)

        st.session_state.pop('pending_join_code', None)


main()