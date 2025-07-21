import re
import pandas as pd

import re
import pandas as pd

def preprocess(data):
    # Pattern for timestamped messages
    pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - (.+)"
    matches = re.findall(pattern, data)

    users = []
    messages = []
    dates = []
    times = []

    for date, time, chat in matches:
        date_obj = pd.to_datetime(date.strip(), dayfirst=True)
        time_obj = pd.to_datetime(time.strip(), format='%H:%M').time()

        if ':' in chat:
            user, message = chat.split(':', 1)
            user = user.strip()
            if user == "Meta AI":
                continue
            users.append(user)
            messages.append(message.strip())
        else:
            users.append("group_notification")
            messages.append(chat.strip())

        dates.append(date_obj)
        times.append(time_obj)

    df = pd.DataFrame({
        'user': users,
        'message': messages,
        'date': dates,
        'time': times
    })

    # Extract year, month, day, hour, minute
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day.astype(str).str.zfill(2)
    df['hour'] = pd.to_datetime(df['time'].astype(str), format='%H:%M:%S').dt.hour.astype(str).str.zfill(2)
    df['minute'] = pd.to_datetime(df['time'].astype(str), format='%H:%M:%S').dt.minute.astype(str).str.zfill(2)

    return df

