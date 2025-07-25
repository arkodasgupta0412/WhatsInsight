import streamlit as st
import preprocessor, helper
import animation
import draw  
import time
from wordCloud import plot_wordCloud
import seaborn as sns
import helper


def get_user_colors(user_counts):
    users = list(user_counts.keys())
    palette = sns.color_palette("hls", len(users))
    user_color_map = {user: palette[i] for i, user in enumerate(users)}

    return user_color_map



def setTitle():
    st.sidebar.markdown(
        "<h1 style='font-size: 32px; font-family: monospace; margin-top: 0; margin-bottom: 50px;'>WhatsInsight</h1>",
        unsafe_allow_html=True)
    


def setGap(level="subheading"):
    if level == "heading":
        gap = 40
    else:
        gap = 30
    st.markdown(f"<div style='margin-top: {gap}px;'></div>", unsafe_allow_html=True)



def setPageConfig():
    st.set_page_config(page_title="WhatsInsight", layout="wide")
    hide_streamlit_style = """<style>#MainMenu {visibility: hidden;}
                                .stDeployButton {display:none;}
                                footer {visibility: hidden;}
                                #stDecoration {display:none;}
                              </style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)



def user_selection_sidebar(df):
    user_list = helper.extract_users(df)
    selected_user = st.sidebar.selectbox("Select participant", user_list, key="user_selector")
    analyze = st.sidebar.button("Show Insights")

    return selected_user, analyze



def upload_and_preprocess_chat():
    st.sidebar.write("Curious what your chats reveal? Upload to find out!")

    uploaded_file = st.sidebar.file_uploader("Choose a file")

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        st.sidebar.success("File uploaded successfully!")

        df = preprocessor.preprocess(data)
        # st.write(df.columns.tolist())
        # st.dataframe(df)
        return df
    return None



def basic_statistics(df, selected_user):

    if selected_user == "Overall":
        group_created_date = helper.group_created(df)
        participants = helper.member_count(df)
        formatted_date = group_created_date.strftime("%d %B %Y") if group_created_date else "Not Available"

        group_age = time.time() - group_created_date.timestamp() if group_created_date else 0
        days = group_age // 86400
        years = int(days // 365.25)
        remaining_days = days % 365.25
        months = int(remaining_days // 30.44)
        days = int(remaining_days % 30.44)

        st.markdown(f"""<div style='font-size:18px; font-family: monospace; font-weight:500; padding:6px 0; margin-bottom:16px;'>
                <b>Group Created On: </b><span style='color:#1f77b4;'>{formatted_date}</span>
                </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div style='font-size:18px; font-family: monospace; font-weight:500; padding:6px 0; margin-bottom:16px;'>
                <b>Group Age: </b><span style='color:#1f77b4;'>{years} yrs {months} months {days} days</span>
                </div>""", unsafe_allow_html=True)
        
        st.markdown(f"""<div style='font-size:18px; font-family: monospace; font-weight:500; padding:6px 0; margin-bottom:16px;'>
                <b>Number of Participants: </b><span style='color:#1f77b4;'>{participants}</span>
                </div>""", unsafe_allow_html=True)
        setGap()

    # Shared: Metrics Section
    avg_len = helper.avg_msg_length(selected_user, df)
    longest_msg = helper.longest_message(selected_user, df)
    wordstock = helper.unique_words_used(selected_user, df)

    col1, col2, col3, col4 = st.columns(4)

    total_messages = helper.messages_sent(selected_user, df)
    total_words = helper.words_typed(selected_user, df)
    total_links = helper.links_shared(selected_user, df)
    total_media = helper.media_shared(selected_user, df)

    metric_data = [
        (col1, "Text Messages Sent", total_messages),
        (col2, "Words Typed", total_words),
        (col3, "Links Shared", total_links),
        (col4, "Media Shared", total_media),
    ]

    animation.numerical_metrics(metric_data)

    col1.caption(f"Average text message length: {avg_len} words")
    col1.caption(f"Longest text message: {longest_msg} words")
    col1.caption(f"WordStock (Unique words typed): {wordstock}")
    setGap()


    # Emoji section
    st.markdown("#### Emojis Used")
    emoji_stats = helper.emojis_used(selected_user, df)
    #print(helper.emojis_used(selected_user, df))
    col1, col2 = st.columns(2)
    animation.numerical_metrics([(col1, "Total Emojis Used", emoji_stats['total_emojis_used'])])

    col2.metric("Most Used Emoji", emoji_stats['most_used_emoji'])
    setGap()



def user_analysis(df, selected_user):
    file_has_media = helper.is_media_included(df)

    if selected_user == "Overall":
        # -------------------------
        # Overall User Analysis
        # -------------------------

        # First Row: Top active users and message distributions
        col1, spacer, col2 = st.columns([5, 1, 5])

        # Column 1: Bar chart
        with col1:
            st.markdown("#### Top Active Users")
            fig1 = draw.top_active_users_plot(df)
            st.pyplot(fig1)

        # Column 2: Pie chart
        with col2:
            st.markdown("#### Text Messages Distribution (%)")
            fig2 = draw.distribution_chart(df, "messages")
            st.pyplot(fig2)


        # Second Row: media and link distributions
        col3, spacer, col4 = st.columns([5, 1, 5])

        with col3:
            setGap()
            st.markdown("#### Media Distribution (%)")
            fig3 = draw.distribution_chart(df, "media")
            st.pyplot(fig3)

        with col4:
            setGap()
            st.markdown("#### Links Distribution (%)")
            fig4 = draw.distribution_chart(df, "links")
            st.pyplot(fig4)


        # Media categorization, images, video, audio, doc + contact -> Third Row
        if (file_has_media):
            
            col5, spacer3, col6 = st.columns([5, 1, 5])

            with col5:
                setGap()
                st.markdown("#### Media Categorization")
                fig5 = draw.plot_media_categorization(df, "Overall")
                st.pyplot(fig5)


            with col6:
                setGap()
                image_count, video_count, audio_count, doc_count, contact_count = helper.count_media_docs_contacts(df, "Overall")

                setGap()
                setGap()
                setGap()
                setGap()
                st.markdown(f"##### Images shared: &nbsp;&nbsp; {image_count}")
                st.markdown(f"##### Videos shared: &nbsp;&nbsp; {video_count}")
                st.markdown(f"##### Audios shared: &nbsp;&nbsp; {audio_count}")
                st.markdown(f"##### Documents shared: &nbsp;&nbsp; {doc_count}")
                st.markdown(f"##### Contacts shared: &nbsp;&nbsp; {contact_count}")
            

    else:
        # -------------------------
        # Individual user analysis
        # -------------------------

        user_df = df[df["user"] == selected_user]

        # Row 1: Most Active Year, Month, Day
        st.markdown("#### Most Active")
        col1, col2, col3 = st.columns(3)

        most_year, most_month, most_day = helper.most_active_times(user_df)
        most_day = most_day.strftime("%d %B %Y")


        with col1:
            st.markdown("<p style='margin-bottom: 0.2rem;'><b>Year</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 1.6rem; margin-top: 0.2rem;'>{most_year}</p>", unsafe_allow_html=True)

        with col2:
            st.markdown("<p style='margin-bottom: 0.2rem;'><b>Month</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 1.6rem; margin-top: 0.2rem;'>{most_month}</p>", unsafe_allow_html=True)

        with col3:
            st.markdown("<p style='margin-bottom: 0.2rem;'><b>Day</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 1.6rem; margin-top: 0.2rem;'>{most_day}</p>", unsafe_allow_html=True)

        setGap()

        # 2nd row -> Media categorization, images, video, audio
        if (file_has_media):
            
            col4, spacer3, col5 = st.columns([5, 1, 5])

            with col4:
                setGap()
                st.markdown("#### Media Categorization")
                fig1 = draw.plot_media_categorization(df, selected_user)
                st.pyplot(fig1)

            
            with col5:
                setGap()
                image_count, video_count, audio_count, doc_count, contact_count = helper.count_media_docs_contacts(df, selected_user)

                setGap()
                setGap()
                setGap()
                setGap()
                st.markdown(f"##### Images shared: &nbsp;&nbsp; {image_count}")
                st.markdown(f"##### Videos shared: &nbsp;&nbsp; {video_count}")
                st.markdown(f"##### Audios shared: &nbsp;&nbsp; {audio_count}")
                st.markdown(f"##### Documents shared: &nbsp;&nbsp; {doc_count}")
                st.markdown(f"##### Contacts shared: &nbsp;&nbsp; {contact_count}")

            setGap()
            setGap()


        # Row 3: Line plots
        col6, spacer1, col7, spacer2, col8 = st.columns([5, 1, 5, 1, 5])

        with col6:
            st.markdown("#### Yearly Activity")
            fig1 = draw.yearly_message_count_plot(user_df)
            st.pyplot(fig1)

        with col7:
            st.markdown("#### Monthly Activity")
            fig2 = draw.monthly_message_count_plot(user_df)
            st.pyplot(fig2)

        with col8:
            st.markdown("#### Weekly Activity")
            fig3 = draw.weekday_message_count_plot(user_df)
            st.pyplot(fig3)      



def temporal_activity(df, selected_user):
    if selected_user == "Overall":
        setGap()
        overall_df = df[df['user'] != 'group_notification']

        col1, spacer1, col2, spacer2, col3 = st.columns([5, 1, 5, 1, 5])

        with col1:
            st.markdown("#### Yearly Activity")
            fig1 = draw.yearly_message_count_plot(overall_df)
            st.pyplot(fig1)

        with col2:
            st.markdown("#### Monthly Activity")
            fig2 = draw.avg_monthly_message_count_plot(overall_df)
            st.pyplot(fig2)

        with col3:
            st.markdown("#### Weekly Activity")
            fig3 = draw.avg_weekday_message_count_plot(overall_df)
            st.pyplot(fig3)

        setGap()
        st.markdown("#### Hourly Activity")
        setGap()
        fig4 = draw.hourly_message_count_plot(overall_df)
        st.pyplot(fig4)

    else:
        col1, col2, col3, col4 = st.columns(4)
        
        first_msg_date = helper.first_message_date(selected_user, df)
        last_msg_date = helper.last_message_date(selected_user, df)
        longest_active_streak = helper.longest_active_streak(selected_user, df)
        longest_inactive_streak = helper.longest_inactive_streak(selected_user, df)

        # Format dates
        first_msg_str = first_msg_date.strftime("%d %B %Y") if first_msg_date else "N/A"
        last_msg_str = last_msg_date.strftime("%d %B %Y") if last_msg_date else "N/A"

        metric_data = [
            (col3, "Longest Active Streak", longest_active_streak, "days"),
            (col4, "Longest Inactive Streak", longest_inactive_streak, "days"),
        ]

        with col1:
            st.write("First Text")  
            st.write(first_msg_str)

        with col2:
            st.write("Last Text")
            st.write(last_msg_str)

        animation.numerical_metrics(metric_data)

        setGap()
        st.markdown("#### Hourly Activity")
        setGap()
        fig4 = draw.hourly_message_count_plot(df, selected_user)
        st.pyplot(fig4)



def wordCloud(df, selected_user):
    plot_wordCloud(df, selected_user, message_column='message')
        


def concluding_analysis(df, selected_user):
    col1, spacer, col2 = st.columns([5, 1, 5])

    with col1:
        st.markdown("##### Response Time Distribution")
        st.write(
            "**Note:** For clarity, response times exceeding 25 minutes are excluded from the plot. "
            "However, the true average may still be higher."
        )
        rt_data = helper.response_times(df)
        fig = draw.response_time_plot(rt_data["all_deltas"], rt_data["avg"])
        st.pyplot(fig)


    with col2:
        st.markdown("##### Day vs Night Activity")
        fig_pie = draw.plot_day_night_activity_pie(df, selected_user)
        st.pyplot(fig_pie, use_container_width=True)



def chat_timeline(df):    
    setGap()
    st.markdown("#### Chat Timeline")
    setGap()

    fig = draw.plot_chat_timeline(df)
    st.pyplot(fig)