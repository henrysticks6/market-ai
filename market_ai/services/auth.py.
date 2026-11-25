
import streamlit as st
from supabase import create_client


APP_URL = "https://market-ai-bkgv5tzjyqfracyyab77bp.streamlit.app/"


def get_supabase():
    # Keep each browser session's Supabase client separate.
    if "market_ai_supabase_client" not in st.session_state:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")

        if not url or not key:
            raise RuntimeError(
                "Supabase URL or publishable key is missing from Streamlit Secrets."
            )

        st.session_state["market_ai_supabase_client"] = create_client(
            url, key
        )

    return st.session_state["market_ai_supabase_client"]


def register_user(surname, first_name, email, phone, password):
    supabase = get_supabase()

    return supabase.auth.sign_up({
        "email": email.strip().lower(),
        "password": password,
        "options": {
            "email_redirect_to": APP_URL,
            "data": {
                "surname": surname.strip(),
                "first_name": first_name.strip(),
                "phone": phone.strip()
            }
        }
    })


def login_user(email, password):
    supabase = get_supabase()

    return supabase.auth.sign_in_with_password({
        "email": email.strip().lower(),
        "password": password
    })


def reset_password(email):
    supabase = get_supabase()

    return supabase.auth.reset_password_for_email(
        email.strip().lower(),
        {"redirect_to": APP_URL}
    )


def logout_user():
    try:
        get_supabase().auth.sign_out()
    finally:
        for key in [
            "market_ai_authenticated",
            "market_ai_user_email",
            "market_ai_user_id"
        ]:
            st.session_state.pop(key, None)


def require_authentication():
    if st.session_state.get("market_ai_authenticated"):
        return True

    st.markdown(
        """
        <div style="
            padding: 28px;
            border-radius: 18px;
            background: linear-gradient(120deg,#10243A,#1677D2,#16A36A);
            color: white;
            text-align: center;
            margin-bottom: 24px;
        ">
            <h1 style="color:white;">🌐 MARKET AI</h1>
            <h3 style="color:white;">Every Business Deserves a Voice.</h3>
            <p style="color:white;">
                Sign in or create your account to enter your creative workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    login_tab, signup_tab, reset_tab = st.tabs([
        "Login",
        "Create account",
        "Forgot password"
    ])

    with login_tab:
        st.subheader("Welcome back")

        with st.form("market_ai_login_form"):
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button(
                "Login",
                type="primary",
                use_container_width=True
            )

        if submitted:
            if not email.strip() or not password:
                st.warning("Enter your email address and password.")
            else:
                try:
                    response = login_user(email, password)

                    if response.session and response.user:
                        st.session_state["market_ai_authenticated"] = True
                        st.session_state["market_ai_user_email"] = response.user.email
                        st.session_state["market_ai_user_id"] = response.user.id
                        st.success("Login successful.")
                        st.rerun()
                    else:
                        st.error(
                            "Login could not be completed. Please confirm your email "
                            "address and try again."
                        )

                except Exception as error:
                    st.error(f"Login failed: {error}")

    with signup_tab:
        st.subheader("Create your MARKET AI account")

        with st.form("market_ai_signup_form"):
            surname = st.text_input("Surname")
            first_name = st.text_input("First name")
            email = st.text_input("Email address")
            phone = st.text_input(
                "Phone number",
                placeholder="e.g. 08012345678"
            )
            password = st.text_input("Create password", type="password")
            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Create account",
                type="primary",
                use_container_width=True
            )

        if submitted:
            if not all([
                surname.strip(),
                first_name.strip(),
                email.strip(),
                phone.strip(),
                password,
                confirm_password
            ]):
                st.warning("Please complete all the registration fields.")

            elif "@" not in email or "." not in email.split("@")[-1]:
                st.warning("Enter a valid email address.")

            elif len(password) < 6:
                st.warning("Your password must contain at least 6 characters.")

            elif password != confirm_password:
                st.error("Your passwords do not match.")

            else:
                try:
                    with st.spinner("Creating your account..."):
                        response = register_user(
                            surname,
                            first_name,
                            email,
                            phone,
                            password
                        )

                    if response.session:
                        st.success(
                            "Your account has been created. You can now log in."
                        )
                    else:
                        st.success(
                            "Registration submitted! Check your email and click "
                            "the confirmation link before logging in."
                        )

                except Exception as error:
                    st.error(f"Registration failed: {error}")

    with reset_tab:
        st.subheader("Reset your password")

        with st.form("market_ai_reset_form"):
            reset_email = st.text_input("Your registered email address")

            submitted = st.form_submit_button(
                "Send password reset email",
                type="primary",
                use_container_width=True
            )

        if submitted:
            if not reset_email.strip():
                st.warning("Enter your registered email address.")
            else:
                try:
                    reset_password(reset_email)
                    st.success(
                        "If the account exists, a password reset email has been sent."
                    )
                except Exception as error:
                    st.error(f"Could not send reset email: {error}")

    st.caption(
        "By creating an account, you agree to use MARKET AI responsibly. "
        "Your phone number is collected for account records; SMS verification "
        "will be introduced in a later phase."
    )

    return False


def show_logout_button():
    if st.button("Log out", key="market_ai_logout"):
        logout_user()
        st.rerun()
