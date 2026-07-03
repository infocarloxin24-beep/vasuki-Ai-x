# analysis.py - Saare 4 feature ek saath
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import Counter
import urllib.parse

# ================== WHATSAPP SHARE BUTTON WITH ICON ==================
def add_whatsapp_share_button():
    app_url = "https://infocarloxin24-beep.streamlit.app" # 👈 Yahan apna Streamlit app ka URL daal
    text = "X Profile Bot Scanner 🔥 TPD, Heatmap, Spam check karo free me!"
    wa_link = f"https://wa.me/?text={urllib.parse.quote(text)}%20{app_url}"

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f'<a href="{wa_link}" target="_blank" style="text-decoration:none;">'
        f'<div style="background:#25D366;color:white;padding:12px;border-radius:8px;text-align:center;font-weight:600;width:100%;cursor:pointer;margin-bottom:10px;">'
        f'<img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20" style="vertical-align:middle;margin-right:8px;">'
        f'Share Tool on WhatsApp'
        f'</div></a>',
        unsafe_allow_html=True
    )

# ================== FEATURE 1: TIME HEATMAP ==================
def show_time_heatmap(timestamps):
    st.subheader("1. Posting Time Heatmap")
    if not timestamps:
        st.warning("No timestamp data")
        return 0

    df = pd.DataFrame({'time': pd.to_datetime(timestamps)})
    df['hour'] = df['time'].dt.hour
    df['day'] = df['time'].dt.day_name()

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
    heatmap_data = heatmap_data.reindex(days)

    fig = px.imshow(heatmap_data,
                    labels=dict(x="Hour", y="Day", color="Tweets"),
                    color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

    night_posts = df[df['hour'].between(2, 5)].shape[0]
    night_percent = (night_posts / len(df)) * 100 if len(df) > 0 else 0
    st.metric("Night Activity 2-5AM", f"{night_percent:.1f}%")
    return night_percent

# ================== FEATURE 2: DUPLICATE CHECK ==================
def check_duplicate_content(tweets):
    st.subheader("2. Content Duplicate Check")
    if not tweets:
        st.warning("No tweet data")
        return 0

    tweet_counts = Counter(tweets)
    total_tweets = len(tweets)
    unique_tweets = len(tweet_counts)

    duplicate_count = total_tweets - unique_tweets
    duplicate_percent = (duplicate_count / total_tweets) * 100 if total_tweets > 0 else 0

    st.metric("Duplicate Content", f"{duplicate_percent:.1f}%")
    with st.expander("Top Repeated Tweets"):
        for text, count in tweet_counts.most_common(3):
            if count > 1:
                st.write(f"**{count}x:** {text[:80]}...")

    return duplicate_percent

# ================== FEATURE 3: INTERVAL ANALYSIS ==================
def interval_analysis(timestamps):
    st.subheader("3. Interval Analysis")
    if len(timestamps) < 2:
        st.warning("Need at least 2 tweets for interval analysis")
        return 1.0

    df = pd.DataFrame({'time': pd.to_datetime(timestamps)})
    df = df.sort_values('time')
    df['diff'] = df['time'].diff().dt.total_seconds()
    df = df.dropna()

    if df.empty:
        st.warning("Not enough data")
        return 1.0

    mean_interval = df['diff'].mean()
    std_interval = df['diff'].std()
    cv = std_interval / mean_interval if mean_interval > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Gap", f"{mean_interval/3600:.1f} hrs")
    col2.metric("Interval CV", f"{cv:.2f}")

    if cv < 0.5:
        col3.error("Bot-like: Too Regular")
    else:
        col3.success("Human-like")

    fig = px.histogram(df, x='diff', nbins=50, title="Time Between Posts")
    st.plotly_chart(fig, use_container_width=True)

    return cv

# ================== FEATURE 4: SIDEBAR SHARE ==================
def init_sidebar_history():
    if 'scan_history' not in st.session_state:
        st.session_state.scan_history = []

def save_to_history(username, tpd, bot_score, night_pct, dup_pct, cv):
    st.session_state.scan_history.insert(0, {
        'username': username,
        'tpd': tpd,
        'bot_score': bot_score,
        'night': night_pct,
        'duplicate': dup_pct,
        'cv': cv
    })
    st.session_state.scan_history = st.session_state.scan_history[:10]

def show_sidebar_share():
    st.sidebar.title("4. Recent Scans & Share")
    add_whatsapp_share_button() # 👈 Yahan WhatsApp button with icon add ho gaya

    if not st.session_state.scan_history:
        st.sidebar.info("No scans yet")
        return

    for scan in st.session_state.scan_history:
        col1, col2 = st.sidebar.columns([5, 1])

        with col1:
            st.markdown(f"**@{scan['username']}**")
            st.caption(f"Risk: {scan['bot_score']:.0f}% | TPD: {scan['tpd']:.1f}")

        with col2:
            share_text = f"""*Bot Audit: @{scan['username']}*
TPD: {scan['tpd']:.1f}
Bot Risk: {scan['bot_score']:.0f}%
Night Posts: {scan['night']:.1f}%
Duplicate: {scan['duplicate']:.1f}%
Interval CV: {scan['cv']:.2f}
Checked via BotCheck"""

            encoded = urllib.parse.quote(share_text)
            wa_url = f"https://wa.me/?text={encoded}"
            st.link_button("↗️", wa_url)

        st.sidebar.divider()

# ================== MASTER FUNCTION ==================
def run_all_analysis(username, tweet_times_list, tweet_text_list, tpd):
    """Ye ek function call karte hi saare 4 feature chal jayenge"""
    init_sidebar_history()
    show_sidebar_share() # Ye WhatsApp button + history dono dikhayega

    night_pct = show_time_heatmap(tweet_times_list)
    dup_pct = check_duplicate_content(tweet_text_list)
    cv = interval_analysis(tweet_times_list)

    # Bot score calculate
    bot_score = (night_pct * 0.4) + (dup_pct * 0.4) + ((1-cv) * 20 if cv<1 else 0)
    bot_score = min(100, max(0, bot_score))

    st.metric("Overall Bot Risk Score", f"{bot_score:.0f}%")

    # Sidebar me save
    save_to_history(username, tpd, bot_score, night_pct, dup_pct, cv)
    return bot_score
