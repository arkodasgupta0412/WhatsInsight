import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from collections import Counter
import streamlit as st
from draw import STREAMLIT_BG

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall',
    'this', 'that', 'these', 'those', 'here', 'there', 'where', 'when', 'why', 'how',
    'not', 'no', 'yes', 'ok', 'okay', 'yeah', 'yep', 'nope', 'uh', 'um', 'oh', 'ah', 'edited',
    'so', 'now', 'then', 'well', 'just', 'really', 'very', 'too', 'also', 'only',
    'get', 'got', 'go', 'going', 'come', 'coming', 'know', 'think', 'see', 'look',
    'like', 'want', 'need', 'make', 'take', 'give', 'put', 'say', 'tell', 'ask',
    'one', 'two', 'three', 'first', 'last', 'good', 'bad', 'big', 'small', 'new', 'old',
    'right', 'left', 'up', 'down', 'back', 'away', 'out', 'off', 'over', 'under', 'media', 'omitted', 'message', 'deleted', 'text',
    'messages', 'endtoend', 'encrypted', 'chat', 'whatsapp', 'whats', 'app', 'whatsappchat', 'whatsappmessages', 'whatsappmessage',
}



def setGap(level="subheading"):
    if level == "heading":
        gap = 40
    else:
        gap = 30
    st.markdown(f"<div style='margin-top: {gap}px;'></div>", unsafe_allow_html=True)



def clean_text(text):
    """ Clean and preprocess text for word cloud generation """

    if pd.isna(text) or text == '':
        return ''
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers
    # Matches: 1234567890, 123-456-7890, 123.456.7890, (123) 456-7890, +91 1234567890, etc.
    text = re.sub(r'[\+]?[\d\s\-\.\(\)]{10,15}', '', text)
    
    # Remove any remaining standalone 10+ digit numbers
    text = re.sub(r'\b\d{10,}\b', '', text)
    
    # Remove special characters and numbers, keep only letters and spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespaces
    text = ' '.join(text.split())
    
    return text



def get_top_words(text_data, top_n=50, min_length=2):
    """ Extract top N words from text data """

    # Combine all text
    all_text = ' '.join(text_data.dropna().astype(str))
    
    # Clean the text
    cleaned_text = clean_text(all_text)
    
    if not cleaned_text:
        return {}
    
    # Split into words and filter
    words = cleaned_text.split()
    words = [word for word in words if len(word) >= min_length and word not in STOP_WORDS]
    
    # Count words and get top N
    word_counts = Counter(words)
    top_words = dict(word_counts.most_common(top_n))
    
    return top_words



def generate_wordcloud(df, selected_user="Overall", message_column='message', top_n=50, width=800, height=400, background_color='black', colormap='viridis', max_font_size=100):
    """ Generate a word cloud from message data """
 
    df_copy = df.copy()
    
    # Filter by user if not "Overall"
    if selected_user != "Overall":
        user_columns = ['user', 'name', 'sender', 'from']
        user_col = None
        
        for col in user_columns:
            if col in df_copy.columns:
                user_col = col
                break
        
        if user_col:
            df_copy = df_copy[df_copy[user_col] == selected_user]
            print(f"Filtered to user '{selected_user}': {len(df_copy)} messages")
        else:
            print("Warning: No user column found, showing overall data")
    
    # Check if message column exists
    if message_column not in df_copy.columns:
        available_cols = [col for col in df_copy.columns if 'message' in col.lower() or 'text' in col.lower() or 'content' in col.lower()]
        if available_cols:
            message_column = available_cols[0]
            print(f"Using column '{message_column}' for messages")
        else:
            print(f"Error: No suitable message column found. Available columns: {list(df_copy.columns)}")
            return None
    
    if len(df_copy) == 0:
        print(f"No messages found for user '{selected_user}'")
        return None
    
    # Get top words
    print(f"Processing {len(df_copy)} messages...")
    word_freq = get_top_words(df_copy[message_column], top_n=top_n)
    
    if not word_freq:
        print("No words found after filtering")
        return None
    
    print(f"Top 10 words: {dict(list(word_freq.items())[:10])}")
    
    # Create word cloud
    try:
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color=background_color,
            colormap=colormap,
            max_font_size=max_font_size,
            relative_scaling=0.5,
            random_state=42,
            collocations=False,  # Avoid pairing words
            max_words=top_n
        ).generate_from_frequencies(word_freq)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(width/100, height/100))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        
        # Set title
        # title = f"Word Cloud - Top {top_n} Words"
        # if selected_user != "Overall":
        #    title += f" ({selected_user})"
        # else:
        #    title += " (Overall)"
            
        # fig.suptitle(title, fontsize=16, color='white', y=0.95)
        fig.patch.set_facecolor('none')
        
        plt.tight_layout()

        return fig
        
    except Exception as e:
        print(f"Error generating word cloud: {e}")

        return None



def get_word_freq_table(df, selected_user="Overall", message_column='message', top_n=50):
    """ Get a frequency table of top words """

    df_copy = df.copy()
    
    user_columns = ['user', 'name', 'sender', 'from']
    user_col = None
    for col in user_columns:
        if col in df_copy.columns:
            user_col = col
            break

    # Filter to remove system-generated messages
    if user_col:
        df_copy = df_copy[df_copy[user_col] != 'group_notification']
        if selected_user != "Overall":
            df_copy = df_copy[df_copy[user_col] == selected_user]
    else:
        print("Warning: No user-identifying column found, skipping user filtering")
    
    # Check message column
    if message_column not in df_copy.columns:
        available_cols = [col for col in df_copy.columns if 'message' in col.lower() or 'text' in col.lower()]
        if available_cols:
            message_column = available_cols[0]
    
    # Get word frequencies
    word_freq = get_top_words(df_copy[message_column], top_n=top_n)
    
    if not word_freq:
        return pd.DataFrame()
    
    # Convert to DataFrame
    freq_df = pd.DataFrame(list(word_freq.items()), columns=['Word', 'Frequency'])
    freq_df['Rank'] = range(1, len(freq_df) + 1)
    
    return freq_df[['Rank', 'Word', 'Frequency']]



def plot_wordCloud(df, selected_user="Overall", message_column='message'):
    """ Display word cloud in Streamlit with enhanced readability for dark backgrounds """

    setGap()
    st.subheader("WordCloud")
    setGap()
    
    # Fixed parameters
    top_n = 100
    colormap = "Set3"
    width = 500
    height = 200
    max_font_size = 120
    bg_color = STREAMLIT_BG

    # Generate word cloud
    fig = generate_wordcloud(
        df,
        selected_user=selected_user,
        message_column=message_column,
        top_n=top_n,
        width=width,
        height=height,
        background_color=bg_color,
        colormap=colormap,
        max_font_size=max_font_size
    )

    if fig:
        st.pyplot(fig, use_container_width=True)
    else:
        st.error("Could not generate word cloud. Check your data format.")
