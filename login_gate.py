y load failed: {str(e)[:50]}") 


st.markdown("📧 *Feedback:* [nishadsingh00@gmail.com](mailto:nishadsingh00@gmail.com?subject=HumBotix%20Feedback)")
with col2:
    with st.expander("🔐 User Login / Sign Up"):
        try:
            session = supabase.auth.get_session()
            current_user = session.user if session else None
        except:
            current_user = None

        if current_user:
            st.success(f"✅ Logged in as: {current_user.email}")
            user_meta = current_user.user_metadata if hasattr(current_user, 'user_metadata') else {}
            display_name = user_meta.get('full_name', current_user.email.split('@')[0])
            st.write(f"Name: {display_name}")

            col_out1, col_out2 = st.columns(2)
            with col_out1:
                if st.button("🚪 Logout", use_container_width=True, type="primary"):
                    try:
                        supabase.auth.sign_out()
                        st.success("Logged out successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Logout failed: {e}")

            with col_out2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
        else:
            auth_mode = st.radio("Mode:", ["Login", "Sign Up"], horizontal=True, key="auth_mode")

            if auth_mode == "Login":
                st.markdown("##### 📧 Login with Email")
                email = st.text_input("Email:", key="auth_email_login")
                password = st.text_input("Password:", type="password", key="auth_pass_login")

                if st.button("Login", key="login_submit", use_container_width=True):
                    try:
                        res = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.success("Login Successful! 🎉")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")

            else:
                st.markdown("##### 📝 Create New Account")
                full_name = st.text_input("Full Name:", placeholder="Nishad Singh", key="auth_name_signup")
                email = st.text_input("Email:", key="auth_email_signup")
                password = st.text_input("Password:", type="password", key="auth_pass_signup")

                if st.button("Sign Up", key="signup_submit", use_container_width=True):
                    try:
                        res = supabase.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {"data": {"full_name": full_name}}
                        })
                        st.success("Sign Up Successful! Verify your email 📧")
                        st.info("Verification link sent to your email")
                    except Exception as e:
                        st.error(f"Sign Up failed: {str(e)}")

            st.markdown("---")
            st.markdown("##### 🚀 Social Login")

            st.markdown("""
            <style>
       .social-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                width: 100%;
                padding: 10px;
                margin: 5px 0;
                border: 1px solid #dadce0;
                border-radius: 8px;
                background: white;
                color: #3c4043;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                text-decoration: none;
            }
       .social-btn:hover {
                background: #f8f9fa;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
       .social-btn img {
                width: 20px;
                height: 20px;
            }
            </style>
            """, unsafe_allow_html=True)
