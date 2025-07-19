# Setup Guide for WhatsInsight

Welcome! This guide will walk you through setting up and running **WhatsInsight** — a visual analytics tool for exploring WhatsApp chats.

---

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/WhatsInsight.git
cd WhatsInsight
```

## 2. Create and Activate Conda Environment

```bash
conda create -n whatsinsight python=3.11.13 -y
conda activate whatsinsight
```

## 3. Install dependencies

```bash
conda env update --file environment.yml --name whatsinsight
```

## 4. Run the App

First, set the Python interpreter in the created conda environment as default one. (if not set)
In VS Code, you can click the `Select Interpreter` option shown at the bottom bar.

Then run the app using:

```bash
streamlit run app.py
```

If you're getting "Fatal error in launcher" when using `streamlit run`, ensure that `streamlit` is correctly added to your system PATH and matches the active environment.

Alternatively, you can run the app using the commmand:

```bash
python -m streamlit run app.py
```

## 5. Prepare Your WhatsApp Chat File

1. Open **WhatsApp** on your phone.
2. Go to the **group or personal chat** you want to analyze.
3. Tap on the **chat name** > **More** > **Export Chat**.
4. Choose **Without Media** for better performance.
5. Send the exported `.txt` file to your computer (via email, Google Drive, etc).
6. Upload it using the file uploader in the app’s interface.

---

## 6. How to Use the App

Once the app opens in your browser:

- **Upload** the exported `.txt` chat file.
- **Select "Overall"** from the dropdown to analyze the **entire group**.
- Or, **select a specific user** to see **personalized analytics**.

Explore insightful visualizations like:

- Most active user
- Hourly and weekday activity trends
- Word clouds for frequent terms
  <br>and more...
