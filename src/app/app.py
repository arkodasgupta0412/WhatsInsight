import utils
import streamlit as st


def run():
    utils.setTitle()
    utils.setPageConfig()
    df = utils.upload_and_preprocess_chat()

    if df is not None:
        selected_user, analyze = utils.user_selection_sidebar(df)

        if analyze:
            st.markdown(f"# Insights: `{selected_user}`")
            utils.setGap()
            utils.basic_statistics(df, selected_user)

            if (selected_user == "Overall"):
                utils.setGap()
                timeline = utils.draw.plot_chat_timeline(df)
                utils.st.pyplot(timeline)
                utils.setGap()
                utils.setGap()
         
            utils.user_analysis(df, selected_user)
            utils.setGap()
            utils.temporal_activity(df, selected_user)
            utils.setGap()
            utils.setGap()
            utils.concluding_analysis(df, selected_user);
            utils.setGap()
            utils.wordCloud(df, selected_user)
            utils.setGap()


if __name__ == '__main__':
    run()