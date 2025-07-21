import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns
import pandas as pd
from datetime import datetime
import helper

# Streamlit dark theme background
STREAMLIT_BG = '#0E1117'


def get_user_colors(user_counts):
    users = list(user_counts.keys())
    palette = sns.color_palette("hls", len(users))
    user_color_map = {user: palette[i] for i, user in enumerate(users)}

    return user_color_map



def plot_chat_timeline(df):
    """
    Plots the daily message count timeline.
    """

    df = df[df['user'] != 'group_notification'].copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    daily_counts = df.groupby('date').size()

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor('none')
    ax.set_facecolor(STREAMLIT_BG)

    # Line plot
    ax.plot(daily_counts.index, daily_counts.values, color="#79f245", linewidth=1.3)

    # Title & labels
    ax.set_title("Chat Timeline", fontsize=22, fontweight='bold', color='white', pad=20)
    ax.set_xlabel("", fontsize=12)
    ax.set_ylabel("Messages", fontsize=14, color='white')

    # X-axis formatting (month + year)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', rotation=45, colors='white')
    ax.tick_params(axis='y', colors='white')

    # Clean look
    ax.spines['top'].set_color(STREAMLIT_BG)
    ax.spines['right'].set_color(STREAMLIT_BG)   
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white') 

    plt.tight_layout()

    return fig



def distribution_chart(df, metric):
    valid_metrics = ['messages', 'media', 'links']
    if metric not in valid_metrics:
        raise ValueError(f"Invalid metric '{metric}'. Choose from {valid_metrics}")

    if metric == 'messages':
        user_counts = df['user'].value_counts().to_dict()
    elif metric == 'media':
        user_counts = df[df['message'] == '<Media omitted>']['user'].value_counts().to_dict()
    elif metric == 'links':
        user_counts = df[df['message'].str.contains(r'https?://', na=False)]['user'].value_counts().to_dict()

    user_counts = {
        user: count for user, count in user_counts.items()
        if user.lower() != 'group_notification' and user.lower() != 'meta ai'
    }

    if not user_counts:
        raise ValueError(f"No data available for metric '{metric}'.")

    sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
    top_users = sorted_users[:7]
    other_users = sorted_users[7:]
    top_labels, top_sizes = zip(*top_users) if top_users else ([], [])
    other_total = sum(count for _, count in other_users)

    if other_total > 0:
        labels = list(top_labels) + ['Others']
        sizes = list(top_sizes) + [other_total]
    else:
        labels = list(top_labels)
        sizes = list(top_sizes)

    total = sum(sizes)

    user_color_map = get_user_colors(user_counts)
    colors = [user_color_map.get(user, '#999999') for user in labels]

    raw_percentages = [count / total * 100 for count in sizes]
    rounded_percentages = np.floor(raw_percentages).astype(int)
    diff = 100 - sum(rounded_percentages)
    remainders = np.array(raw_percentages) - rounded_percentages
    for i in np.argsort(remainders)[-diff:]:
        rounded_percentages[i] += 1

    streamlit_bg = STREAMLIT_BG
    fig, ax = plt.subplots(figsize=(5.5, 5.5), dpi=100)
    fig.patch.set_facecolor(streamlit_bg)
    ax.set_facecolor(streamlit_bg)

    sorted_items = sorted(zip(labels, sizes, colors, rounded_percentages), key=lambda x: x[0])
    labels, sizes, colors, rounded_percentages = zip(*sorted_items)

    wedges, _ = ax.pie(
        rounded_percentages,
        labels=None,
        startangle=90,
        counterclock=False,
        colors=colors,
        wedgeprops=dict(width=0.4)
    )
    ax.axis('equal')

    ax.text(0, 0, "100", ha='center', va='center',
            fontsize=18, color='white', fontweight='bold')

    radius = 0.8
    for i, wedge in enumerate(wedges):
        theta = 0.5 * (wedge.theta1 + wedge.theta2)
        angle_rad = np.deg2rad(theta)
        x = radius * np.cos(angle_rad)
        y = radius * np.sin(angle_rad)
        ax.text(x, y, f"{rounded_percentages[i]}",
                ha='center', va='center',
                fontsize=12, color='black', fontweight='bold')

    legend_labels = [f"{label}" for label in labels]
    num_cols = 2 if len(legend_labels) <= 6 else 3 if len(legend_labels) <= 12 else 4

    legend = ax.legend(
        wedges, legend_labels,
        title="Participants",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),  
        fontsize=10,
        title_fontsize=12,
        ncol=num_cols,
        frameon=False,
        labelspacing=1.0,
        handlelength=1.2
    )
    for text in legend.get_texts():
        text.set_color("white")
    legend.get_title().set_color("white")

    fig.tight_layout(pad=2.0)

    return fig



def top_active_users_plot(df):
    df = df[df['user'].str.lower() != 'group_notification']

    user_counts = df['user'].value_counts()
    top_users = user_counts.head(min(5, len(user_counts)))

    user_color_map = get_user_colors(user_counts)

    colors = [user_color_map[user] for user in top_users.index]

    fig, ax = plt.subplots(figsize=(9, 9.4))

    fig.patch.set_facecolor('none')         
    fig.patch.set_edgecolor('none')        

    ax.set_facecolor(STREAMLIT_BG)          
    ax.spines['top'].set_color(STREAMLIT_BG)
    ax.spines['right'].set_color(STREAMLIT_BG)   
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')        

    # Plot bars
    bars = ax.bar(top_users.index, top_users.values, color=colors)

    ax.tick_params(axis='x', colors='white', labelsize=15)
    ax.tick_params(axis='y', colors='white', labelsize=15)

    # Title
    ax.set_xlabel("Participants", color='white', fontsize=18, labelpad=30)
    ax.set_ylabel("Text Messages", color='white', fontsize=18, labelpad=30)
    # ax.set_title("Top Active Users", color='white', fontsize=12)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height * 0.5,
            f"{int(height)}",
            ha='center',
            va='center',
            color='white',
            fontsize=15,
            fontweight='bold'
        )

    fig.patch.set_edgecolor('none')

    return fig


def yearly_message_count_plot(df):
    year_counts = df['year'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(9, 9.4))

    # Match background
    fig.patch.set_facecolor('none')
    fig.patch.set_edgecolor('none')
    ax.set_facecolor(STREAMLIT_BG)

    # Match spines
    ax.spines['top'].set_color(STREAMLIT_BG)
    ax.spines['right'].set_color(STREAMLIT_BG)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')

    # Plot line
    ax.plot(year_counts.index, year_counts.values, marker='o', color='skyblue', linewidth=2)

    # X & Y ticks
    ax.set_xticks(year_counts.index)  # Show only actual years
    ax.tick_params(axis='x', colors='white', labelsize=15)
    ax.tick_params(axis='y', colors='white', labelsize=15)

    # Labels
    ax.set_xlabel("Year", color='white', fontsize=18, labelpad=30)
    ax.set_ylabel("Text Messages", color='white', fontsize=18, labelpad=30)
    ax.set_title("Yearly Text Messages Count", color='white', fontsize=18, pad=20)

    # Add value labels on markers
    for x, y in zip(year_counts.index, year_counts.values):
        ax.text(x, y, str(y), color='white', fontsize=15, ha='center', va='bottom', fontweight='bold')

    return fig


def monthly_message_count_plot(df):
    # Extract month
    df['month'] = pd.to_datetime(df['date']).dt.strftime('%B')

    # Month order 
    month_order = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]

    # Count messages per month
    month_counts = df['month'].value_counts().reindex(month_order, fill_value=0)

    # Create short month names for display
    short_months = [month[:3] for month in month_order]

    fig, ax = plt.subplots(figsize=(9, 9.4))

    # Match background
    fig.patch.set_facecolor('none')
    fig.patch.set_edgecolor('none')
    ax.set_facecolor(STREAMLIT_BG)

    # Match spines
    ax.spines['top'].set_color(STREAMLIT_BG)
    ax.spines['right'].set_color(STREAMLIT_BG)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')

    # Plot line
    ax.plot(short_months, month_counts.values, marker='o', color='lightgreen', linewidth=2)

    # X & Y ticks
    ax.set_xticks(short_months)
    ax.tick_params(axis='x', colors='white', labelsize=13, rotation=45)
    ax.tick_params(axis='y', colors='white', labelsize=15)

    # Labels
    ax.set_xlabel("Month", color='white', fontsize=18, labelpad=30)
    ax.set_ylabel("Text Messages", color='white', fontsize=18, labelpad=30)
    ax.set_title("Monthly Text Messages Count", color='white', fontsize=18, pad=20)

    # Add value labels
    for x, y in zip(short_months, month_counts.values):
        if not pd.isna(y):
            ax.text(x, y, str(int(y)), color='white', fontsize=14, ha='center', va='bottom', fontweight='bold')

    return fig



def weekday_message_count_plot(df):
    # Extract full weekday names
    df['weekday'] = df['date'].dt.day_name()

    # Define full weekday order
    weekday_order_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_counts = df['weekday'].value_counts().reindex(weekday_order_full)

    # Convert to short form for display
    weekday_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_counts.index = weekday_short

    fig, ax = plt.subplots(figsize=(9, 9.4))

    fig.patch.set_facecolor('none')
    fig.patch.set_edgecolor('none')
    ax.set_facecolor(STREAMLIT_BG)

    ax.spines['top'].set_color(STREAMLIT_BG)
    ax.spines['right'].set_color(STREAMLIT_BG)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')

    ax.plot(weekday_counts.index, weekday_counts.values, marker='o', color='orange', linewidth=2)

    ax.set_xticks(weekday_counts.index)
    ax.tick_params(axis='x', colors='white', labelsize=13, rotation=45)
    ax.tick_params(axis='y', colors='white', labelsize=15)

    ax.set_xlabel("Weekday", color='white', fontsize=18, labelpad=30)
    ax.set_ylabel("Text Messages", color='white', fontsize=18, labelpad=30)
    ax.set_title("Weekday Text Messages Count", color='white', fontsize=18, pad=20)

    for x, y in zip(weekday_counts.index, weekday_counts.values):
        if not pd.isna(y):
            ax.text(x, y, str(int(y)), color='white', fontsize=14, ha='center', va='bottom', fontweight='bold')

    return fig



def avg_monthly_message_count_plot(df):
    # Convert month to short form  (January -> Jan)
    df['month_short'] = df['month'].apply(lambda x: datetime.strptime(x, "%B").strftime("%b"))

    # Group by year and short month name, count, then take mean over years
    monthly_avg = (
        df.groupby(['year', 'month_short'])
        .size()
        .groupby(level=1)
        .mean()
        .reindex([
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ])
    )

    fig, ax = plt.subplots(figsize=(9, 9.4))

    # Match background
    fig.patch.set_facecolor('none')
    fig.patch.set_edgecolor('none')
    ax.set_facecolor(STREAMLIT_BG)

    # Match spines
    ax.spines['top'].set_color(STREAMLIT_BG)
    ax.spines['right'].set_color(STREAMLIT_BG)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')

    # Plot line
    ax.plot(monthly_avg.index, monthly_avg.values, marker='o', color='yellow', linewidth=2)

    # X & Y ticks
    ax.set_xticks(monthly_avg.index)
    ax.tick_params(axis='x', colors='white', labelsize=13, rotation=45)
    ax.tick_params(axis='y', colors='white', labelsize=15)

    # Labels
    ax.set_xlabel("Month", color='white', fontsize=18, labelpad=30)
    ax.set_ylabel("Avg Text Messages", color='white', fontsize=18, labelpad=30)
    ax.set_title("Average Monthly Text Messages", color='white', fontsize=18, pad=20)

    # Add value labels on markers
    for x, y in zip(monthly_avg.index, monthly_avg.values):
        if not pd.isna(y):
            ax.text(x, y, f"{y:.0f}", color='white', fontsize=14, ha='center', va='bottom', fontweight='bold')

    return fig


def avg_weekday_message_count_plot(df):
    df['weekday'] = df['date'].dt.day_name().str[:3]
    df['week'] = df['date'].dt.isocalendar().week
    df['year'] = df['date'].dt.year

    weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Group by weekday and count messages
    weekday_counts = df.groupby('weekday').size()

    # Count how many unique week-year combos each weekday appears in
    weekday_weeks = df.groupby(['weekday'])[['year', 'week']].nunique()
    weekday_weeks = weekday_weeks['week'].reindex(weekday_order).fillna(1)

    # Compute average messages per weekday
    avg_counts = (weekday_counts // weekday_weeks).reindex(weekday_order).fillna(0)

    fig, ax = plt.subplots(figsize=(9, 9.4))
    fig.patch.set_facecolor('none')
    fig.patch.set_edgecolor('none')
    ax.set_facecolor(STREAMLIT_BG)

    ax.spines['top'].set_color(STREAMLIT_BG)
    ax.spines['right'].set_color(STREAMLIT_BG)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')

    ax.plot(avg_counts.index, avg_counts.values, marker='o', color='pink', linewidth=2)

    ax.set_xticks(avg_counts.index)
    ax.tick_params(axis='x', colors='white', labelsize=13, rotation=45)
    ax.tick_params(axis='y', colors='white', labelsize=15)

    ax.set_xlabel("Weekday", color='white', fontsize=18, labelpad=30)
    ax.set_ylabel("Avg Text Messages", color='white', fontsize=18, labelpad=30)
    ax.set_title("Average Weekday Text Messages", color='white', fontsize=18, pad=20)

    for x, y in zip(avg_counts.index, avg_counts.values):
        ax.text(x, y, f"{y:.1f}", color='white', fontsize=14, ha='center', va='bottom', fontweight='bold')

    return fig


def hourly_message_count_plot(df, selected_user="Overall"): 
    df_copy = df.copy()
    
    if selected_user != "Overall":
        if 'user' in df_copy.columns:
            df_copy = df_copy[df_copy['user'] == selected_user]
            print(f"Filtered to user '{selected_user}': {len(df_copy)} messages")
        elif 'name' in df_copy.columns:
            df_copy = df_copy[df_copy['name'] == selected_user]
            print(f"Filtered to user '{selected_user}': {len(df_copy)} messages")
        elif 'sender' in df_copy.columns:
            df_copy = df_copy[df_copy['sender'] == selected_user]
            print(f"Filtered to user '{selected_user}': {len(df_copy)} messages")
        else:
            print("Warning: No user/name/sender column found, showing overall data")
    
    if len(df_copy) == 0:
        print(f"No messages found for user '{selected_user}'")
        return None
    
    if 'time' in df_copy.columns and 'date' in df_copy.columns:
        try:
            df_copy['datetime'] = pd.to_datetime(df_copy['date'].astype(str) + ' ' + df_copy['time'].astype(str))
            df_copy['hour'] = df_copy['datetime'].dt.hour
        except:
            df_copy['hour'] = df_copy['time'].astype(str).str[:2].astype(int)
    

    elif 'date' in df_copy.columns:
        try:
            df_copy['hour'] = pd.to_datetime(df_copy['date']).dt.hour
        except:
            print("Error parsing date column")
            return None

    elif 'time' in df_copy.columns:
        df_copy['hour'] = df_copy['time'].astype(str).str[:2].astype(int)
    
    else:
        print("No suitable time/date column found")
        return None
    

    # Ensure hour values are valid (0-23)
    df_copy = df_copy[(df_copy['hour'] >= 0) & (df_copy['hour'] <= 23)]
    

    # Debug: Check the hour extraction 
    print(f"Hour range: {df_copy['hour'].min()} to {df_copy['hour'].max()}") 
    print(f"Unique hours: {sorted(df_copy['hour'].unique())}") 
    print(f"Total messages after filtering: {len(df_copy)}") 
     

    # Group by hour and get total messages per hour 
    hourly_counts = df_copy.groupby('hour').size().reindex(range(24), fill_value=0) 
     
    print(f"Hourly counts: {hourly_counts.to_dict()}") 
    print(f"Max hourly count: {hourly_counts.max()}") 
    

    # Check if we have any data
    if hourly_counts.sum() == 0:
        print("WARNING: No messages found in any hour!")
        print("Check your data format and time/date columns")
        return None
 
    # 12-hour format labels 
    hour_labels = [] 
    for h in range(24): 
        next_h = (h + 1) % 24 
        hour_labels.append(f"{helper.format_hour(h)} - {helper.format_hour(next_h)}") 
 
    # Plotting 
    fig, ax = plt.subplots(figsize=(16, 10)) 
    fig.patch.set_facecolor('none') 
    ax.set_facecolor(STREAMLIT_BG) 
 
    # Bars
    bars = ax.bar( 
        range(24), 
        hourly_counts.values,
        color='skyblue', 
        width=0.8,  
        align='center',
        edgecolor='white', 
        linewidth=0.5,
        alpha=0.8 
    ) 
 
    ax.set_xlim(-0.5, 23.5) 
    max_count = hourly_counts.max()
    ax.set_ylim(0, max_count * 1.2 if max_count > 0 else 10) 
 
    # X-axis ticks 
    ax.set_xticks(range(24)) 
    ax.set_xticklabels(hour_labels, rotation=45, fontsize=11, color='white', ha='right') 
 
    ax.tick_params(axis='y', colors='white', labelsize=13) 
    ax.set_xlabel("Hour", color='white', fontsize=16, labelpad=20) 
    ax.set_ylabel("Total Messages", color='white', fontsize=16, labelpad=20) 
    # ax.set_title(f"Hourly Text Messages", color='white', fontsize=18, pad=20) 
 
    # Remove top/right spines 
    ax.spines['top'].set_color(STREAMLIT_BG) 
    ax.spines['right'].set_color(STREAMLIT_BG) 
    ax.spines['left'].set_color('white') 
    ax.spines['bottom'].set_color('white') 
 
    # Remove any grid 
    ax.grid(False) 
 
    # Annotate bars 
    for i, v in enumerate(hourly_counts.values): 
        if v > 0: 
            ax.text(i, v + max_count * 0.02, f"{int(v)}", 
                   ha='center', va='bottom', color='white', fontsize=10, 
                   fontweight='bold') 
 
    plt.tight_layout() 

    return fig



def response_time_plot(response_times, avg, max_display_cap=25):
    """Plots a histogram of response times with dynamic x and y scale adjustments."""

    # Determine dynamic x-limit based on actual data
    max_response_time = response_times.max()
    x_limit = min(max_response_time, max_display_cap)

    # Add 10-15% buffer for aesthetics
    x_limit_buffer = int(np.ceil(x_limit * 1.15))
    x_limit = min(x_limit_buffer, max_display_cap)

    # Filter out extreme outliers
    filtered = response_times[response_times <= x_limit]

    # Compute histogram bins
    counts, bin_edges = np.histogram(filtered, bins=50)

    # Determine dynamic y-limit based on peak frequency
    y_max = counts.max()
    y_limit = int(np.ceil(y_max * 1.15))

    # Plot
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor('none')
    ax.set_facecolor(STREAMLIT_BG)

    ax.hist(filtered, bins=50, color="#ca43d6")

    # Axes config
    ax.set_xlim([0, x_limit])
    ax.set_ylim([0, y_limit])
    ax.set_xlabel("Response Time (minutes)", color='white', fontsize=14, labelpad=20)
    ax.set_ylabel("Frequency", color='white', fontsize=14, labelpad=20)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['top'].set_color(STREAMLIT_BG)
    ax.spines['right'].set_color(STREAMLIT_BG)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')

    # Title
    hr = int(avg // 60)
    mn = int(round(avg) - (hr * 60))
    # ax.set_title(f"Average Response Time: {hr} hrs {mn} mins", fontsize=13, color='white', pad=20)

    return fig



def heatmap_weekday_vs_hour(df, selected_user="Overall"):
    """
    Draws a gradient heatmap showing message counts by day of week and hour of day.
    """

    if selected_user == "Overall":
        df = df[df['user'] != 'group_notification'].copy()
    else:
        df = df[df['user'] == selected_user].copy()

    # Ensure hour is numeric
    df['hour'] = pd.to_numeric(df['hour'], errors='coerce').fillna(0).astype(int)

    # Create day name column (Monday, Tuesday, ...)
    df['day_name'] = pd.to_datetime(df['date'], errors='coerce').dt.day_name()

    # Count messages grouped by weekday and hour
    heatmap_data = df.groupby(['day_name', 'hour']).size().unstack(fill_value=0)

    # Reorder and map weekdays
    full_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    short_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    heatmap_data = heatmap_data.reindex(full_days)

    # Convert 24-hour to 12-hour format
    hour_labels = [f"{(h % 12 or 12)} {'AM' if h < 12 else 'PM'}" for h in heatmap_data.columns]
    heatmap_data.columns = hour_labels

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor('none')
    ax.set_facecolor('#0E1117')

    sns.heatmap(
        heatmap_data,
        cmap='YlOrBr',
        ax=ax,
        cbar=True,
        cbar_kws={'label': 'Messages'},
        linewidths=0,
        annot=False
    )

    # Label and style
    ax.set_xlabel("Hour", labelpad=12)
    ax.set_ylabel("Weekday", labelpad=12)
    ax.set_yticklabels(short_days, rotation=0)

    ax.tick_params(colors='white', labelsize=10)
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

    # Style colorbar
    colorbar = ax.collections[0].colorbar
    colorbar.ax.yaxis.label.set_color('white')
    colorbar.ax.tick_params(colors='white')

    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()

    return fig



def plot_day_night_activity_pie(df, selected_user="Overall"):
    """
    Plots a pie chart showing day vs. night message distribution.
    Day: 6 AM - 5:59 PM
    Night: 6 PM - 5:59 AM
    """

    if selected_user == "Overall":
        df = df[df['user'] != 'group_notification']
    else:
        df = df[df['user'] == selected_user]

    df['hour'] = pd.to_numeric(df['hour'], errors='coerce').fillna(0).astype(int)

    # Classify hours into Day and Night
    df['period'] = df['hour'].apply(lambda hour: 'Day' if 6 <= hour < 18 else 'Night')
    counts = df['period'].value_counts().to_dict()
    counts.setdefault("Day", 0)
    counts.setdefault("Night", 0)

    labels = ['Day', 'Night']
    sizes = [counts['Day'], counts['Night']]
    colors = ["#ecf235", "#272AED"] 

    fig, ax = plt.subplots()
    fig.patch.set_facecolor('none')
    ax.set_facecolor('#0E1117')

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        startangle=90,
        autopct='%1.1f%%',
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )

    for i, label in enumerate(labels):
        if label == 'Day':
            texts[i].set_color('black')
            autotexts[i].set_color('black')
        else:
            texts[i].set_color('white')
            autotexts[i].set_color('white')

    return fig

