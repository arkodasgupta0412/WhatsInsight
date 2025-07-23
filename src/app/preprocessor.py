import re
import pandas as pd


def update_ios_system_messages(df):
    system_message_patterns = [
        r"Messages and calls are end-to-end encrypted",
        r"changed the subject", 
        r"added", 
        r"left", 
        r"removed", 
        r"changed this group's icon",
        r"joined using this group's invite link", 
        r"deleted this message",
        r"created group", 
        r"video call", 
        r"Missed voice call", 
        r"Missed video call",
        r"this message was deleted", 
        r"changed the group description",
        r"Everyone is requested to reach the venue atlea", 
        r"Please join this group",
        r"https://chat\.whatsapp\.com/",
        r"You were added",
        r"security code changed",
        r"now an admin",
        r"no longer an admin"
    ]

    system_regex = re.compile("|".join(system_message_patterns), re.IGNORECASE)

    system_message_mask = df['message'].str.contains(system_regex, na=False)
    
    df.loc[system_message_mask, 'user'] = "group_notification"
    
    return df



def preprocess(data):
    # Combining both iOS and Android regex patterns
    pattern = r"""
        (?:                             # non-capturing group for full match
            \[?                         # optional opening bracket (iOS)
            (?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s* # date
            (?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*[APMapm\.]*)  # time with optional seconds + AM/PM
            \]?                         # optional closing bracket (iOS)
            (?:\s*[\-\]]\s*)            # separator (- or ])
            (?P<chat>.+)                # user and message
        )
    """

    matches = re.finditer(pattern, data, re.VERBOSE)

    users = []
    messages = []
    dates = []
    times = []

    for match in matches:
        date = match.group("date")
        time = match.group("time").replace('\u202f', ' ').strip()
        chat = match.group("chat").strip()

        try:
            date_obj = pd.to_datetime(date.strip(), dayfirst=True, errors='coerce')
            if pd.isna(date_obj):
                continue

            # Normalize time (detect AM/PM or 24-hr)

            # 12-hour format
            if re.search(r'[APMapm]', time):  
                time_obj = pd.to_datetime(time, format='%I:%M:%S %p', errors='coerce')
                if pd.isna(time_obj):
                    time_obj = pd.to_datetime(time, format='%I:%M %p', errors='coerce')

            # 24-hour format
            else:  
                time_obj = pd.to_datetime(time, format='%H:%M:%S', errors='coerce')
                if pd.isna(time_obj):
                    time_obj = pd.to_datetime(time, format='%H:%M', errors='coerce')

            if pd.isna(time_obj):
                continue

            time_obj = time_obj.time()

            if ':' in chat:
                user, message = chat.split(':', 1)
                user = user.strip()
                if user.lower() == "meta ai":
                    continue
                users.append(user)
                messages.append(message.strip())
            else:
                users.append("group_notification")
                messages.append(chat.strip())

            dates.append(date_obj)
            times.append(time_obj)

        except Exception:
            continue

    # Create dataframe
    df = pd.DataFrame({
        'user': users,
        'message': messages,
        'date': dates,
        'time': times
    })

    # Extract components
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day.astype(str).str.zfill(2)
    df['hour'] = pd.to_datetime(df['time'].astype(str), format='%H:%M:%S').dt.hour.astype(str).str.zfill(2)
    df['minute'] = pd.to_datetime(df['time'].astype(str), format='%H:%M:%S').dt.minute.astype(str).str.zfill(2)

    df = update_ios_system_messages(df)

    return df

