import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")

# FontAwesome CDN - Icons ke liye
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">', unsafe_allow_html=True)

# Session state
if 'open_report' not in st.session_state:
    st.session_state.open_report = None
if 'scan_history' not in st.session_state:
    st.session_state.scan_history = []

def calculate_bot_score(data):
    posts_per_day = data.get('posts_per_day', 0)
    if posts_per_day > 50:
        verdict = "High Risk Bot"
        bot_score = 85
        color = "#f87171"
        desc = "This account shows strong signs of automated behavior."
    elif posts_per_day > 20:
        verdict = "Suspicious"
        bot_score = 60
        color = "#fbbf24"
        desc = "This account shows some suspicious patterns."
    else:
        verdict = "Human"
        bot_score = 20
        color = "#4ade80"
        desc = "This account appears to be operated by a human."
    
    data.update({
        'bot_score': bot_score, 'verdict': verdict, 'verdict_color': color, 'verdict_desc': desc
    })
    return data

def get_score_color_label(score):
    if score >= 70: return "#4ade80", "Good", "fa-circle-check"
    elif score >= 40: return "#fbbf24", "Suspicious", "fa-triangle-exclamation"
    elif score > 0: return "#f87171", "Poor", "fa-circle-xmark"
    else: return "#64748b", "Not Verified", "fa-circle-question"

def show_compact_row(data, idx):
    col1, col2, col3, col4 = st.columns([0.5, 3, 2, 1.5])
    with col1:
        st.image(f"https://ui-avatars.com/api/?name={data['username']}&background=8b5cf6&color=fff", width=35)
    with col2:
        st.markdown(f"*@{data['username']}*")
        st.caption(f"{data['platform']} • {data['scan_time']}")
    with col3:
        st.markdown(f"<span style='color:{data['verdict_color']}; font-size:14px; font-weight:600;'>{data['bot_score']}% {data['verdict']}</span>", unsafe_allow_html=True)
    with col4:
        if st.button("View Report", key=f"view_{idx}", use_container_width=True):
            st.session_state.open_report = None if st.session_state.open_report == idx else idx
            st.rerun()

    if st.session_state.open_report == idx:
        st.markdown("---")
        show_full_card(data, idx)
        st.markdown("---")

def show_full_card(data, idx):
    st.markdown("""
    <style>
    .main-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 24px; color: white; font-family: 'Segoe UI', sans-serif; }
    .top-section { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; margin-bottom: 20px; }
    .profile-box { background: #0b1220; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; display: flex; gap: 20px; }
    .pfp-ring { width: 90px; height: 90px; background: linear-gradient(45deg, #ec4899, #8b5cf6, #3b82f6); padding: 3px; border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.8; } }
    .pfp-ring img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; border: 2px solid #0b1220; }
    .bot-score-box { background: #1a0b0b; border: 1px solid #3f1212; border-radius: 12px; padding: 20px; text-align: center; }
    .bot-score-val { font-size: 56px; font-weight: 700; color: #f87171; margin: 8px 0; line-height: 1; }
    .progress-bar { width: 100%; height: 6px; background: #374151; border-radius: 3px; margin-top: 12px; }
    .progress-fill { height: 100%; background: #f87171; border-radius: 3px; transition: width 1s ease; }
    .metrics-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; background: #0b1220; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 20px; }
    .metric-item { text-align: center; }
    .metric-bar { width: 100%; height: 4px; background: #374151; border-radius: 2px; margin: 8px 0; }
    .metric-fill { height: 100%; border-radius: 2px; transition: width 0.8s ease; }
    .bottom-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    .info-box { background: #0b1220; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; }
    .summary-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #1e293b; }
    .recommend-box { background: #0b1220; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; }
    .footer-box { background: #064e3b; border: 1px solid #059669; border-radius: 12px; padding: 16px; display: flex; justify-content: space-between; align-items: center; }
    .share-btn { background: #1e293b; border: 1px solid #334155; color: #94a3b8; padding: 8px 16px; border-radius: 8px; cursor: pointer; }
    .icon-pulse { animation: iconPulse 2s infinite; }
    @keyframes iconPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
    </style>
    """, unsafe_allow_html=True)

    u_color, u_label, u_icon = get_score_color_label(data['username_score'])
    p_color, p_label, p_icon = get_score_color_label(data['profile_score'])
    a_color, a_label, a_icon = get_score_color_label(data['activity_score'])
    e_color, e_label, e_icon = get_score_color_label(data['engagement_score'])
    b_color, b_label, b_icon = get_score_color_label(data['bio_score'])
    v_color, v_label, v_icon = get_score_color_label(data['verify_score'])

    card_html = f"""
    <div class="main-card">
        <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
            <div>
                <h2 style="margin:0;">Scan Result</h2>
                <p style="margin:0; color:#94a3b8; font-size:14px;">Completed on {data['scan_time']}</p>
            </div>
            <button class="share-btn"><i class="fas fa-sync-alt"></i> New Scan</button>
        </div>

        <div class="top-section">
            <div class="profile-box">
                <div class="pfp-ring">
                    <img src="https://ui-avatars.com/api/?name={data['username']}&background=8b5cf6&color=fff">
                </div>
                <div style="flex:1;">
                    <h3 style="margin:0 0 8px 0;">@{data['username']} <i class="fas fa-check-circle" style="color:#38bdf8;"></i></h3>
                    <div style="background:#1e293b; padding:4px 10px; border-radius:6px; display:inline-block; margin-bottom:12px; font-size:13px;">
                        <i class="fab fa-instagram"></i> {data['platform']}
                    </div>
                    <p style="margin:4px 0; color:#94a3b8; font-size:14px;"><i class="fas fa-user" style="color:#94a3b8;"></i> Username: @{data['username']}</p>
                    <p style="margin:4px 0; color:#94a3b8; font-size:14px;"><i class="fas fa-globe" style="color:#94a3b8;"></i> Platform: {data['platform']}</p>
                    <p style="margin:4px 0; color:#94a3b8; font-size:14px;"><i class="fas fa-clock" style="color:#94a3b8;"></i> Scanned At: {data['scan_time']}</p>
                </div>
            </div>

            <div class="bot-score-box">
                <p style="margin:0; color:#94a3b8; font-size:14px;"><i class="fas fa-robot fa-beat" style="color:#f87171;"></i> Bot Score</p>
                <h1 class="bot-score-val">{data['bot_score']}%</h1>
                <p style="margin:0; color:{data['verdict_color']}; font-weight:600;">{data['verdict']}</p>
                <div class="progress-bar"><div class="progress-fill" style="width:{data['bot_score']}%"></div></div>
                <p style="margin:12px 0 0 0; color:#94a3b8; font-size:12px;">{data['verdict_desc']}</p>
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-item">
                <p style="margin:0; color:#a78bfa; font-size:12px;"><i class="fas fa-user icon-pulse" style="color:{u_color};"></i> Username</p>
                <h3 style="margin:4px 0; color:{u_color}; font-size:28px;">{data['username_score']}<span style="color:#64748b; font-size:16px;">/100</span></h3>
                <div class="metric-bar"><div class="metric-fill" style="width:{data['username_score']}%; background:{u_color};"></div></div>
                <p style="margin:0; color:{u_color}; font-size:12px;">{u_label}</p>
            </div>
            <div class="metric-item">
                <p style="margin:0; color:#60a5fa; font-size:12px;"><i class="fas fa-id-card icon-pulse" style="color:{p_color};"></i> Profile Complete</p>
                <h3 style="margin:4px 0; color:{p_color}; font-size:28px;">{data['profile_score']}<span style="color:#64748b; font-size:16px;">/100</span></h3>
                <div class="metric-bar"><div class="metric-fill" style="width:{data['profile_score']}%; background:{p_color};"></div></div>
                <p style="margin:0; color:{p_color}; font-size:12px;">{p_label}</p>
            </div>
            <div class="metric-item">
                <p style="margin:0; color:#fbbf24; font-size:12px;"><i class="fas fa-chart-line icon-pulse" style="color:{a_color};"></i> Activity Pattern</p>
                <h3 style="margin:4px 0; color:{a_color}; font-size:28px;">{data['activity_score']}<span style="color:#64748b; font-size:16px;">/100</span></h3>
                <div class="metric-bar"><div class="metric-fill" style="width:{data['activity_score']}%; background:{a_color};"></div></div>
                <p style="margin:0; color:{a_color}; font-size:12px;">{a_label}</p>
            </div>
            <div class="metric-item">
                <p style="margin:0; color:#4ade80; font-size:12px;"><i class="fas fa-users icon-pulse" style="color:{e_color};"></i> Engagement Quality</p>
                <h3 style="margin:4px 0; color:{e_color}; font-size:28px;">{data['engagement_score']}<span style="color:#64748b; font-size:16px;">/100</span></h3>
                <div class="metric-bar"><div class="metric-fill" style="width:{data['engagement_score']}%; background:{e_color};"></div></div>
                <p style="margin:0; color:{e_color}; font-size:12px;">{e_label}</p>
            </div>
            <div class="metric-item">
                <p style="margin:0; color:#f87171; font-size:12px;"><i class="fas fa-file-lines icon-pulse" style="color:{b_color};"></i> Bio Analysis</p>
                <h3 style="margin:4px 0; color:{b_color}; font-size:28px;">{data['bio_score']}<span style="color:#64748b; font-size:16px;">/100</span></h3>
                <div class="metric-bar"><div class="metric-fill" style="width:{data['bio_score']}%; background:{b_color};"></div></div>
                <p style="margin:0; color:{b_color}; font-size:12px;">{b_label}</p>
            </div>
            <div class="metric-item">
                <p style="margin:0; color:#60a5fa; font-size:12px;"><i class="fas fa-shield-halved icon-pulse" style="color:{v_color};"></i> Verification</p>
                <h3 style="margin:4px 0; color:{v_color}; font-size:28px;">{data['verify_score']}<span style="color:#64748b; font-size:16px;">/100</span></h3>
                <div class="metric-bar"><div class="metric-fill" style="width:{data['verify_score']}%; background:{v_color};"></div></div>
                <p style="margin:0; color:{v_color}; font-size:12px;">{v_label}</p>
            </div>
        </div>

        <div class="bottom-section">
            <div class="info-box">
                <h4 style="margin:0 0 12px 0;"><i class="fas fa-brain" style="color:#a78bfa;"></i> AI Explanation</h4>
                <p style="margin:0 0 16px 0; color:#94a3b8; font-size:13px;">Our AI has analyzed multiple signals from this account and calculated the probability of this account being a bot.</p>
                <div style="border-top:1px solid #1e293b; padding-top:12px;">
                    <p style="margin:8px 0; font-size:13px;"><i class="fas fa-circle-xmark" style="color:#f87171;"></i> <b>Username Pattern</b><br><span style="color:#94a3b8;">Username contains suspicious pattern or uncommon characters.</span></p>
                    <p style="margin:8px 0; font-size:13px;"><i class="fas fa-triangle-exclamation" style="color:#fbbf24;"></i> <b>Low Engagement</b><br><span style="color:#94a3b8;">Very low likes, comments or interactions compared to follower count.</span></p>
                    <p style="margin:8px 0; font-size:13px;"><i class="fas fa-circle-xmark" style="color:#f87171;"></i> <b>Posting Behavior</b><br><span style="color:#94a3b8;">{data['posts_per_day']} posts/day - {"Irregular pattern" if data['posts_per_day'] > 20 else "Normal pattern"}.</span></p>
                    <p style="margin:8px 0; font-size:13px;"><i class="fas fa-triangle-exclamation" style="color:#fbbf24;"></i> <b>Bio Analysis</b><br><span style="color:#94a3b8;">Bio looks incomplete or contains suspicious keywords.</span></p>
                    <p style="margin:8px 0; font-size:13px;"><i class="fas fa-circle-check" style="color:#4ade80;"></i> <b>Profile Picture</b><br><span style="color:#94a3b8;">Profile picture looks normal.</span></p>
                </div>
            </div>

            <div>
                <div class="info-box" style="margin-bottom:20px;">
                    <h4 style="margin:0 0 12px 0;"><i class="fas fa-file-lines" style="color:#60a5fa;"></i> Account Summary</h4>
                    <div class="summary-row"><span><i class="fas fa-users" style="color:#94a3b8;"></i> Followers</span><span>{data.get('followers', '12.4K')}</span></div>
                    <div class="summary-row"><span><i class="fas fa-user-plus" style="color:#94a3b8;"></i> Following</span><span>{data.get('following', '7,892')}</span></div>
                    <div class="summary-row"><span><i class="fas fa-image" style="color:#94a3b8;"></i> Total Posts</span><span>{data.get('total_posts', '56')}</span></div>
                    <div class="summary-row"><span><i class="fas fa-calendar" style="color:#94a3b8;"></i> Account Created</span><span>{data.get('created', '2 Months Ago')}</span></div>
                    <div class="summary-row"><span><i class="fas fa-chart-column" style="color:#94a3b8;"></i> Avg. Posts/Week</span><span>{data.get('posts_per_week', '0.8')}</span></div>
                    <div class="summary-row" style="border:none;"><span><i class="fas fa-eye" style="color:#94a3b8;"></i> Profile Type</span><span>{data.get('profile_type', 'Public')}</span></div>
                </div>

                <div class="recommend-box">
                    <h4 style="margin:0 0 12px 0;"><i class="fas fa-shield-halved" style="color:#60a5fa;"></i> Our Recommendation</h4>
                    <p style="margin:0; font-size:14px;">This account is <span style="color:{data['verdict_color']}; font-weight:600;">{data['verdict']}</span>.</p>
                    <p style="margin:8px 0 0 0; color:#94a3b8; font-size:13px;">Proceed with caution while interacting with this account.</p>
                </div>
            </div>
        </div>

        <div class="footer-box">
            <div>
                <p style="margin:0; font-weight:600;"><i class="fas fa-circle-check" style="color:#4ade80;"></i> Scan Completed Successfully</p>
                <p style="margin:0; color:#94a3b8; font-size:13px;">This report is generated by Vasuki AI 4.0 - Bot Detector</p>
            </div>
            <button class="share-btn"><i class="fas fa-share-nodes"></i> Share Report</button>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# === MAIN APP ===
st.title("Detector")
st.caption("Multi-Platform Account & Text Scanner | Powered by AI")
tab1, tab2 = st.tabs(["🔍 Bot Check", "🌍 Country Check"])

with tab1:
    st.subheader("Account or Post Scan Karo")
    platform = st.selectbox("सोशल मीडिया प्लेटफॉर्म चुनें:", ["Twitter / X", "Facebook", "Instagram", "YouTube", "LinkedIn"])
    username = st.text_input("Username ya Post URL:")
    
    if st.button("🚀 Scan Now", type="primary"):
        if username:
            dummy_data = {
                'username': username, 'platform': platform,
                'scan_time': datetime.now().strftime("19 Jun 2026, %I:%M %p"),
                'posts_per_day': 65, 'username_score': 40, 'profile_score': 70,
                'activity_score': 30, 'engagement_score': 25, 'bio_score': 45, 'verify_score': 0,
                'followers': '12.4K', 'following': '7,892', 'total_posts': '56',
                'created': '2 Months Ago', 'posts_per_week': '0.8', 'profile_type': 'Public'
            }
            result = calculate_bot_score(dummy_data)
            st.session_state.scan_history.insert(0, result)
            st.rerun()
        else:
            st.error("Username daalo pehle!")

    st.markdown("### 📊 Recent Scans")
    if st.session_state.scan_history:
        for idx, scan in enumerate(st.session_state.scan_history):
            show_compact_row(scan, idx)
            if idx < len(st.session_state.scan_history) - 1: st.divider()
    else:
        st.info("Abhi koi scan nahi hua.")

 Yah code Mein Mujhe onley chahie post timing wali code aur jo screen main aapko bheja tha screenshot vah wala card chahie
