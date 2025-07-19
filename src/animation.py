import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import draw
import io
import random
import streamlit as st


def loading_messages(duration=5):
    messages = [
        "Analyzing chat data...",
        "Crunching numbers...",
        "Gaining insights...",
        "Processing patterns...",
        "Finding the most talkative...",
        "Mapping emojis...",
        "Detecting active hours...",
        "Counting words and media...",
        "Exploring message timelines...",
        "Hang tight, magic is happening..."
    ]

    placeholder = st.empty()
    start_time = time.time()

    while time.time() - start_time < duration:
        msg = random.choice(messages)
        placeholder.markdown(f"<h3 style='color:#00c0f0;'>⏳ {msg}</h3>", unsafe_allow_html=True)
        time.sleep(0.8)

    placeholder.empty()


def numerical_metrics(metric_data, steps=20, delay=0.05):
    placeholders = [col.empty() for col, *_ in metric_data]

    # Animating together in sync
    for i in range(1, steps + 1):
        for idx, metric_info in enumerate(metric_data):
            # Handle both 3-tuple and 4-tuple formats
            if len(metric_info) == 3:
                col, label, final_value = metric_info
                unit = None
            else:
                col, label, final_value, unit = metric_info
            
            interpolated_value = int(final_value * i / steps)
            if unit:
                placeholders[idx].metric(label, f"{interpolated_value} {unit}")
            else:
                placeholders[idx].metric(label, interpolated_value)
        time.sleep(delay)

    # Ensuring final values are set
    for idx, metric_info in enumerate(metric_data):
        if len(metric_info) == 3:
            col, label, final_value = metric_info
            unit = None
        else:
            col, label, final_value, unit = metric_info
            
        if unit:
            placeholders[idx].metric(label, f"{final_value} {unit}")
        else:
            placeholders[idx].metric(label, final_value)


def bars(df):
    df = df[df['user'].str.lower() != 'group_notification']
    user_counts = df['user'].value_counts()
    top_users = user_counts.head(min(5, len(user_counts)))
    user_color_map = draw.get_user_colors(user_counts)

    users = list(top_users.index)
    values = list(top_users.values)
    colors = [user_color_map[user] for user in users]

    fig, ax = plt.subplots(figsize=(9, 9.4))
    fig.patch.set_facecolor('none')
    ax.set_facecolor(draw.STREAMLIT_BG)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white', labelsize=15)
    ax.tick_params(axis='y', colors='white', labelsize=15)
    ax.set_ylim(0, max(values) * 1.1)
    ax.set_xlabel("Participants", color='white', fontsize=18, labelpad=30)
    ax.set_ylabel("Text Messages", color='white', fontsize=18, labelpad=30)

    bars = ax.bar(users, [0]*len(values), color=colors)
    labels = [ax.text(bar.get_x() + bar.get_width()/2, 0, "", 
                      ha='center', va='center', color='white', 
                      fontsize=18, fontweight='bold') for bar in bars]

    def update(frame):
        for i, bar in enumerate(bars):
            height = values[i] * (frame / steps)
            bar.set_height(height)
            labels[i].set_position((bar.get_x() + bar.get_width() / 2, height * 0.5))
            labels[i].set_text(str(int(height)) if height > 0 else "")
        return list(bars) + labels

    steps = 20
    ani = animation.FuncAnimation(fig, update, frames=steps+1, blit=True)

    buf = io.BytesIO()
    ani.save(buf, writer='pillow', fps=20)
    buf.seek(0)
    plt.close(fig)

    return buf