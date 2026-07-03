# analysis.py - Saare 4 feature ek saath
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import Counter
import urllib.parse

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
                st.write(f"*{count}x:* {text[:80]}...")

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
    st.sidebar.title("📜 Live Scan History")

    if not st.session_state.scan_history:
        st.sidebar.info("No scans yet")
        return

    for scan in st.session_state.scan_history:
        with st.sidebar.container():
            # 👇 Har card ka share text - ye WhatsApp pe jayega
            share_text = f"""Bot Audit: @{scan['username']}
Bot Risk: {scan['bot_score']:.0f}%
TPD: {scan['tpd']:.1f}
Night Posts: {scan['night']:.1f}%
Duplicate: {scan['duplicate']:.1f}%
Interval CV: {scan['cv']:.2f}
Scanned via BotCheck: https://humbotix.streamlit.app""" # 👈 Yahan apna URL daal

            encoded = urllib.parse.quote(share_text)
            wa_url = f"https://wa.me/?text={encoded}"

            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(f"*@{scan['username']}*")
                st.caption(f"Risk: {scan['bot_score']:.0f}% | TPD: {scan['tpd']:.1f}")

            with col2:
                # 👇 Tera bheja hua Share icon - chota size 20px
                st.markdown(
                    f'<a href="{wa_url}" target="_blank" title="Share on WhatsApp">'
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-top:8px;cursor:pointer;">'
                    f'<circle cx="18" cy="5" r="3"></circle>'
                    f'<circle cx="6" cy="12" r="3"></circle>'
                    f'<circle cx="18" cy="19" r="3"></circle>'
                    f'<line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>'
                    f'<line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>'
                    f'</svg></a>',
                    unsafe_allow_html=True
                )

        st.sidebar.divider()

# ================== MASTER FUNCTION ==================
def run_all_analysis(username, tweet_times_list, tweet_text_list, tpd):
    """Ye ek function call karte hi saare 4 feature chal jayenge"""
    init_sidebar_history()
    show_sidebar_share() # Ye history + share icon dikhayega

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
