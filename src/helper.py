import time
import re
import emoji
from datetime import timedelta

def format_hour(hr):
    if hr == 0: return "12 A.M"
    elif hr < 12: return f"{hr} A.M"
    elif hr == 12: return "12 P.M"
    else: return f"{hr - 12} P.M"


def extract_users(df):
    user_list = df['user'].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    return user_list


def participant_counts(df):
    return len(extract_users(df)) - 1


def messages_sent(user, df):
    if (user != "Overall"):
        return df[df['user'] == user].shape[0]
    
    else:
        return df[df['user'] != 'group_notification'].shape[0]


def words_typed(user, df):
    if (user != "Overall"):
        user_df = df[df['user'] == user]

    else:
        user_df = df[df['user'] != 'group_notification']

    words_count = user_df['message'].apply(lambda msg: len(str(msg).split())).sum()

    return words_count


def member_count(df):
    return len(extract_users(df)) - 1


def avg_msg_length(user, df):
    return round(words_typed(user, df) / messages_sent(user, df))


def longest_message(user, df):
    if user != "Overall":
        user_df = df[df['user'] == user]
    else:
        user_df = df[df['user'] != 'group_notification']

    user_df['word_count'] = user_df['message'].astype(str).apply(lambda x: len(x.split()))

    longest_msg = user_df['word_count'].max()

    return longest_msg


def unique_words_used(user, df):
    if user != "Overall":
        user_df = df[df['user'] == user]
    else:
        user_df = df[df['user'] != 'group_notification']

    all_messages = " ".join(user_df['message'].astype(str))
    words = re.findall(r'\b\w+\b', all_messages.lower())
    unique_words = set(words)

    return len(unique_words)


def files_shared(user, df):
    if user != "Overall":
        df = df[df['user'] == user]

    patterns = {
        'media': r"<media omitted>",
        'document': r"<document omitted>",
        'gif': r"<gif omitted>",
        'image': r"<image omitted>",
        'video': r"<video omitted>",
    }

    counts = {}

    for label, pattern in patterns.items():
        counts[label] = df['message'].apply(lambda msg: bool(re.search(pattern, str(msg), re.IGNORECASE))).sum()


    counts['total_files_shared'] = sum(counts.values())

    return counts



def media_shared(user, df):
    keyword = "<Media omitted>"

    if (user != "Overall"):
        user_df = df[df['user'] == user]

    else:
        user_df = df.copy()

    media_count = user_df['message'].apply(lambda msg: keyword in str(msg)).sum()

    return media_count


def links_shared(user, df):
    if user != "Overall":
        user_df = df[df['user'] == user]

    else:
        user_df = df[df['user'] != 'group_notification']


    user_df = user_df.dropna(subset=['message'])

    link_pattern = r'(https?://\S+|www\.\S+)'

    link_messages = user_df['message'].astype(str).str.contains(link_pattern, regex=True)

    return link_messages.sum()


def emojis_used(user, df):
    if user != "Overall":
        user_df = df[df['user'] == user]
    else:
        user_df = df[df['user'] != 'group_notification']

    # Concatenate all messages
    all_messages = " ".join(user_df['message'].astype(str))

    # Extract emojis
    emojis_list = [char for char in all_messages if char in emoji.EMOJI_DATA]

    total_emojis = len(emojis_list)

    # Count emojis manually
    emoji_counts = {}
    for e in emojis_list:
        emoji_counts[e] = emoji_counts.get(e, 0) + 1

    # Print emoji frequencies
    # if emoji_counts:
    #    print("Emoji Usage Frequencies:")
    #    for e in sorted(emoji_counts, key=emoji_counts.get, reverse=True):
    #        print(f"{e} : {emoji_counts[e]}")
    # else:
    #   print("No emojis used.")

    # Find most used emoji
    if emoji_counts:
        most_used_emoji = max(emoji_counts, key=emoji_counts.get)
        most_used_emoji_count = emoji_counts[most_used_emoji]
    else:
        most_used_emoji = None
        most_used_emoji_count = 0

    return {
        "total_emojis_used": total_emojis,
        "most_used_emoji": most_used_emoji,
        "most_used_emoji_count": most_used_emoji_count
    }



def group_created(df):
    group_created = df['message'].str.contains("created group", case=False, na=False)

    if group_created.any():
        created_row = df[group_created].iloc[0]
        return created_row['date']
    
    # Fallback: return the timestamp of the first message (for direct messages)
    encryption_pattern = r"Messages and calls are end-to-end encrypted"
    non_encrypted_df = df[~df['message'].str.contains(encryption_pattern, case=False, na=False)]

    if not non_encrypted_df.empty:
        return non_encrypted_df.iloc[0]['date']
    
    return None


def date_joined(user, df):
    pass


def most_active_times(df):
    most_year = df['year'].mode()[0]
    most_month = df['month'].mode()[0]
    most_day = df['date'].dt.date.mode()[0]
    return most_year, most_month, most_day


def messages_per_year(df):
    df['year'] = df['datetime'].dt.year
    return df.groupby('year').size().reset_index(name='message_count')


def avg_messages_per_month(df):
    df['month'] = df['datetime'].dt.month
    monthly_counts = df.groupby(['year', 'month']).size().reset_index(name='message_count')
    avg_monthly = monthly_counts.groupby('month')['message_count'].mean().reset_index()

    return avg_monthly


def avg_messages_per_weekday(df):
    df['weekday'] = df['datetime'].dt.weekday
    weekday_counts = df.groupby(['year', 'month', 'day', 'weekday']).size().reset_index(name='message_count')
    avg_weekday = weekday_counts.groupby('weekday')['message_count'].mean().reset_index()

    return avg_weekday


def first_message_date(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    return df['date'].min()


def last_message_date(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    return df['date'].max()


def longest_active_streak(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    df['date'] = df['date'].dt.date
    active_days = df['date'].drop_duplicates().sort_values()
    max_streak = streak = 1
    for i in range(1, len(active_days)):
        if (active_days.iloc[i] - active_days.iloc[i - 1]) == timedelta(days=1):
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 1

    return max_streak


def longest_inactive_streak(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    df['date'] = df['date'].dt.date
    active_days = df['date'].drop_duplicates().sort_values()
    max_gap = timedelta(days=0)
    for i in range(1, len(active_days)):
        gap = active_days.iloc[i] - active_days.iloc[i - 1]
        if gap > timedelta(days=1):
            max_gap = max(max_gap, gap)

    return max_gap.days



import pandas as pd

def response_times(df):
    """
    Calculates response time (in minutes) between consecutive user messages. Ignores 'group_notification's. """

    user_df = df[df["user"] != "group_notification"].copy()

    # Construct datetime from 'date' and 'time' columns
    user_df['datetime'] = pd.to_datetime(user_df['date'].astype(str) + ' ' + user_df['time'].astype(str), 
                                         errors='coerce')

    # Drop rows where datetime conversion failed (if any)
    user_df.dropna(subset=['datetime'], inplace=True)

    # Sort chronologically
    user_df.sort_values("datetime", inplace=True)

    # Compute time differences in minutes
    user_df['response_time'] = user_df['datetime'].diff().dt.total_seconds() / 60.0

    # Drop the first row which has NaN
    response_times = user_df['response_time'].dropna()

    return {
        "avg": round(response_times.mean(), 2),
        "median": round(response_times.median(), 2),
        "all_deltas": response_times
    }


