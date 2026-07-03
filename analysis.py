# analysis.py - Saare 4 feature ek saath
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import Counter
import urllib.parse
from datetime import datetime

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

# ================== FEATURE 4: SIDEBAR HISTORY + SHARE ICON ==================
def init_sidebar_history():
    if 'scan_history' not in st.session_state:
        st.session_state.scan_history = []

def save_to_history(username, tpd, bot_score, night_pct, dup_pct, cv, age=None, last_tweet=None, total_posts=None, verified=None, flags=None):
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.scan_history.insert(0, {
        'username': username,
        'tpd': tpd,
        'bot_score': bot_score,
        'night': night_pct,
        'duplicate': dup_pct,
        'cv': cv,
        'age': age,
        'last_tweet': last_tweet,
        'total_posts': total_posts,
        'verified': verified,
        'flags': flags,
        'scan_time': scan_time
    })
    st.session_state.scan_history = st.session_state.scan_history[:10]

def show_sidebar_share():
    # 👇 TITLE SIRF 1 BAAR DIKHEGA
    st.sidebar.markdown("### 📜 Live Scan History")

    if not st.session_state.scan_history:
        st.sidebar.info("No scans yet")
        return

    for scan in st.session_state.scan_history:
        with st.sidebar.container():
            verified_text = '✅ Verified' if scan.get('verified') else '❌ Unverified'
            flags = scan.get('flags', 'None')

            share_text = f"""Bot Audit: @{scan['username']}
Bot Risk: {scan.get('bot_score', 0):.0f}%
Tweets/Day: {scan.get('tpd', 0)}
Account Age: {scan.get('age', 'N/A')} days
Last Tweet: {scan.get('last_tweet', 'N/A')}
Total Posts: {scan.get('total_posts', 0)}
Verified: {verified_text}
⚠️ Flags: {flags}
Scanned: https://humbotix.streamlit.app"""

            encoded = urllib.parse.quote(share_text)
            wa_url = f"https://wa.me/?text={encoded}"

            # 👇 CARD + SHARE ICON TOP RIGHT
            st.sidebar.markdown(f"""
            <div style="background:#1E1E1E;padding:12px;border-radius:8px;margin-bottom:12px;position:relative;border:1px solid #2D2D2D;">
                <a href="{wa_url}" target="_blank" title="Share on WhatsApp" style="position:absolute;top:10px;right:10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2">
                        <circle cx="18" cy="5" r="3"></circle>
                        <circle cx="6" cy="12" r="3"></circle>
                        <circle cx="18" cy="19" r="3"></circle>
                        <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                        <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                    </svg>
                </a>
                <p style="margin:0;font-weight:600;color:#FFF;font-size:14px;">@{scan['username']} {scan.get('bot_score', 0):.0f}% Bot</p>
                <p style="margin:6px 0 0 0;color:#9CA3AF;font-size:12px;">📊 Tweets/Day: {scan.get('tpd', 0)}</p>
                <p style="margin:2px 0 0 0;color:#9CA3AF;font-size:12px;">📅 Account Age: {scan.get('age', 'N/A')} days</p>
                <p style="margin:2px 0 0 0;color:#9CA3AF;font-size:12px;">🕒 Last Tweet: {scan.get('last_tweet', 'N/A')}</p>
                <p style="margin:2px 0 0 0;color:#9CA3AF;font-size:12px;">📝 Total Posts: {scan.get('total_posts', 0)}</p>
                <p style="margin:2px 0 0 0;color:#9CA3AF;font-size:12px;">Verified: {verified_text}</p>
                <p style="margin:6px 0 0 0;color:#F59E0B;font-size:12px;">⚠️ Flags:</p>
                <p style="margin:2px 0 0 0;color:#9CA3AF;font-size:11px;white-space:pre-line;">{flags}</p>
                <p style="margin:8px 0 0 0;color:#6B7280;font-size:10px;">{scan.get('scan_time', '')}</p>
            </div>
            """, unsafe_allow_html=True)

# ================== MASTER FUNCTION ==================
def run_all_analysis(username, tweet_times_list, tweet_text_list, tpd, age=None, last_tweet=None, total_posts=None, verified=None, flags=None):
    init_sidebar_history()

    night_pct = show_time_heatmap(tweet_times_list)
    dup_pct = check_duplicate_content(tweet_text_list)
    cv = interval_analysis(tweet_times_list)

    bot_score = (night_pct * 0.4) + (dup_pct * 0.4) + ((1-cv) * 20 if cv<1 else 0)
    bot_score = min(100, max(0, bot_score))

    st.metric("Overall Bot Risk Score", f"{bot_score:.0f}%")

    save_to_history(username, tpd, bot_score, night_pct, dup_pct, cv, age, last_tweet, total_posts, verified, flags)
    show_sidebar_share() # 👈 Sidebar last me render hoga
    return bot_score
