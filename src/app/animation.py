import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from app import draw
import io
import streamlit as st


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
