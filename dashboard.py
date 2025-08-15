import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Customer Contact Centre Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for glassmorphism and neumorphic design
st.markdown("""
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global styles - Dark Theme */
.main .block-container {
    padding: 2rem 3rem !important;
    background: #0f172a !important;
    min-height: 100vh !important;
    font-family: 'Inter', sans-serif !important;
}

/* Ensure full background coverage */
.stApp {
    background: #0f172a !important;
}

/* Main container background fix */
.main {
    background: #0f172a !important;
}

/* Dark theme body */
body {
    background: #0f172a !important;
    color: #e2e8f0 !important;
}

/* Remove Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Sidebar Toggle Button Styling */
button[data-testid="collapsedControl"] {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
    border: 1px solid #475569 !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    padding: 12px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.3s ease !important;
    position: fixed !important;
    top: 20px !important;
    left: 20px !important;
    z-index: 1000 !important;
    width: 48px !important;
    height: 48px !important;
}

button[data-testid="collapsedControl"]:hover {
    background: linear-gradient(135deg, #334155 0%, #475569 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
}

/* Make sure the toggle is always visible */
.stButton[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Sidebar state indicator */
button[data-testid="collapsedControl"]::before {
    content: "🎛️" !important;
    font-size: 20px !important;
}

/* Alternative selectors for the toggle button */
.css-1544g2n button,
.css-r421ms button,
[data-testid="baseButton-headerNoPadding"],
.stSidebar button[kind="headerNoPadding"] {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
    border: 1px solid #475569 !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    padding: 12px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.3s ease !important;
    width: 48px !important;
    height: 48px !important;
}

/* When sidebar is collapsed, show a floating toggle */
.main:not(:has(.stSidebar)) {
    position: relative;
}

.main:not(:has(.stSidebar))::before {
    content: "🎛️";
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 1000;
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border: 1px solid #475569;
    border-radius: 12px;
    color: #ffffff;
    padding: 12px;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Header styling */
.main h1 {
    font-family: 'Inter', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #ffffff;
    text-align: center;
    margin-bottom: 2rem;
}

/* Metric cards - colored gradients */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 20px !important;
    border: none !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
    color: white !important;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4) !important;
}

/* Target the column containers that hold metrics */
.stColumn:nth-child(1) > div {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 20px !important;
    border: none !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
    color: white !important;
}

.stColumn:nth-child(2) > div {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
    border-radius: 20px !important;
    border: none !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
    color: white !important;
}

.stColumn:nth-child(3) > div {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
    border-radius: 20px !important;
    border: none !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
    color: white !important;
}

.stColumn:nth-child(4) > div {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
    border-radius: 20px !important;
    border: none !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
    color: white !important;
}

/* Fix metric text in cards - Enhanced visibility */
.stColumn .metric-label, .stColumn [data-testid="metric-container"] .metric-label {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
}

.stColumn .metric-value, .stColumn [data-testid="metric-container"] .metric-value {
    color: #ffffff !important;
    font-weight: 800 !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
}

/* Fix Streamlit metric labels and values with stronger contrast */
.stColumn [data-testid="metric-container"] label {
    color: #ffffff !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
}

.stColumn [data-testid="metric-container"] [data-testid="metric-value"] {
    color: #ffffff !important;
    font-weight: 800 !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
}

.stColumn [data-testid="metric-container"] div {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Target specific metric elements more aggressively */
.stColumn [data-testid="metric-container"] * {
    color: #ffffff !important;
}

.stColumn div[data-testid="metric-container"] > div {
    color: #ffffff !important;
}

.stColumn div[data-testid="metric-container"] span {
    color: #ffffff !important;
    font-weight: 600 !important;
}

.stColumn div[data-testid="metric-container"] p {
    color: #ffffff !important;
    font-weight: 600 !important;
}

.stColumn > div:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4) !important;
}

/* Chart containers - dark theme */
.element-container {
    background: #1e293b !important;
    border-radius: 16px !important;
    border: 1px solid #334155 !important;
    padding: 20px !important;
    margin-bottom: 20px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}

.element-container:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3) !important;
    transform: translateY(-2px) !important;
}

/* Additional chart container selectors */
.stPlotlyChart {
    background: #1e293b !important;
    border-radius: 16px !important;
    border: 1px solid #334155 !important;
    padding: 20px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}

/* DataFrame styling */
.stDataFrame {
    background: #1e293b !important;
    border-radius: 16px !important;
    border: 1px solid #334155 !important;
    padding: 20px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}

/* DataFrame table styling */
.stDataFrame table {
    background: #1e293b !important;
    color: #e2e8f0 !important;
}

.stDataFrame th {
    background: #334155 !important;
    color: #ffffff !important;
}

.stDataFrame td {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: #334155 !important;
}

/* Modern Sidebar Design - Dark Theme - Fixed Visibility */
section[data-testid="stSidebar"] {
    background: #0f172a !important;
    border: none !important;
    padding: 0 !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

.stSidebar {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

.stSidebar > div {
    background: #0f172a !important;
    padding: 20px !important;
    border: none !important;
    display: block !important;
    visibility: visible !important;
}

/* Sidebar content wrapper */
.stSidebar .block-container {
    background: #0f172a !important;
    padding: 0 !important;
    display: block !important;
    visibility: visible !important;
}

/* Modern filter section headers */
.stSidebar .section-header {
    color: #ffffff !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    margin: 24px 0 16px 0 !important;
    text-align: left !important;
    letter-spacing: 0.5px !important;
}

/* First section header spacing */
.stSidebar .section-header:first-of-type {
    margin-top: 0 !important;
}

/* Tab styling - dark theme */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: #1e293b !important;
    border-radius: 12px !important;
    padding: 6px !important;
    border: 1px solid #334155 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    border: none !important;
    padding: 12px 20px !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: #334155 !important;
    color: #e2e8f0 !important;
}

.stTabs [aria-selected="true"] {
    background: #475569 !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

/* Tab panel styling - Compact for chat */
.stTabs [data-baseweb="tab-panel"] {
    background: #1e293b !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin-top: 8px !important;
    border: 1px solid #334155 !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}

/* Make chat tab extra compact */
.stTabs [data-baseweb="tab-panel"]:has(.section-header:contains("Interactive Chat Assistant")) {
    padding: 8px !important;
    margin-top: 4px !important;
}

/* Modern Filter Components - Dark Theme */

/* Date Input Styling */
.stSidebar .stDateInput > div > div {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease !important;
}

.stSidebar .stDateInput > div > div:hover {
    border-color: #475569 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    transform: translateY(-1px) !important;
}

.stSidebar .stDateInput > div > div:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.stSidebar .stDateInput input {
    background: transparent !important;
    color: #e2e8f0 !important;
    border: none !important;
    font-size: 14px !important;
}

/* Multi-Select Styling */
.stSidebar .stMultiSelect > div > div {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 8px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease !important;
}

.stSidebar .stMultiSelect > div > div:hover {
    border-color: #475569 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    transform: translateY(-1px) !important;
}

.stSidebar .stMultiSelect > div > div:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

/* Multi-select tags */
.stSidebar .stMultiSelect span[data-baseweb="tag"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 4px 8px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}

/* Selectbox Styling */
.stSidebar .stSelectbox > div > div {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease !important;
}

.stSidebar .stSelectbox > div > div:hover {
    border-color: #475569 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    transform: translateY(-1px) !important;
}

.stSidebar .stSelectbox > div > div:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

/* Slider Styling */
.stSidebar .stSlider > div > div {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease !important;
}

.stSidebar .stSlider > div > div:hover {
    border-color: #475569 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

/* Slider track */
.stSidebar .stSlider [data-baseweb="slider"] {
    background: #334155 !important;
}

.stSidebar .stSlider [data-baseweb="slider"] [role="slider"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
}

/* Additional interactive elements */
.stButton > button {
    background: #f0f0f3 !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 4px 4px 8px #d1d1d4, -4px -4px 8px #ffffff !important;
    transition: all 0.3s ease !important;
    color: #333 !important;
    font-weight: 500 !important;
}

.stButton > button:hover {
    box-shadow: 6px 6px 12px #d1d1d4, -6px -6px 12px #ffffff !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    box-shadow: inset 2px 2px 4px #d1d1d4, inset -2px -2px 4px #ffffff !important;
    transform: translateY(0px) !important;
}

/* Text styling - dark theme */
.metric-label {
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 0.9rem;
    font-weight: 500;
}

.metric-value {
    color: white !important;
    font-size: 2rem;
    font-weight: 700;
}

/* Custom glass card - dark theme */
.glass-card {
    background: #1e293b !important;
    border-radius: 16px !important;
    border: 1px solid #334155 !important;
    padding: 20px !important;
    margin: 10px 0 !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    color: #e2e8f0 !important;
}

.section-header {
    color: #ffffff !important;
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Fix chart titles and legends */
.js-plotly-plot .plotly .gtitle {
    fill: #ffffff !important;
}

.js-plotly-plot .plotly .legend {
    fill: #e2e8f0 !important;
}

.js-plotly-plot .plotly text {
    fill: #e2e8f0 !important;
}

/* Fix all Streamlit metric text - Force white */
span[data-testid="metric-value"] {
    color: #ffffff !important;
    font-weight: 800 !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
}

span[data-testid="metric-label"] {
    color: #ffffff !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
}

/* Force all metric container text to be white */
.stColumn [data-testid="metric-container"] {
    color: #ffffff !important;
}

.stColumn [data-testid="metric-container"] > * {
    color: #ffffff !important;
}

.stColumn [data-testid="metric-container"] > * > * {
    color: #ffffff !important;
}

.stColumn [data-testid="metric-container"] > * > * > * {
    color: #ffffff !important;
}

/* Additional metric text fixes */
.metric-container span, .metric-container div {
    color: #ffffff !important;
}

[data-testid="metric-container"] span {
    color: #ffffff !important;
}

[data-testid="metric-container"] div {
    color: #ffffff !important;
}

/* Additional text elements */
.stMarkdown {
    color: #e2e8f0 !important;
}

.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
    color: #ffffff !important;
}

/* Modern Sidebar Text Styling */
.stSidebar .stMarkdown {
    color: #e2e8f0 !important;
}

.stSidebar label {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    margin-bottom: 8px !important;
    display: block !important;
}

/* Input text colors */
.stSidebar .stSelectbox div[data-baseweb="select"] div {
    color: #e2e8f0 !important;
}

.stSidebar .stMultiSelect div[data-baseweb="select"] div {
    color: #e2e8f0 !important;
}

.stSidebar .stSlider div[data-baseweb="slider"] div {
    color: #e2e8f0 !important;
}

/* Dropdown menu styling */
.stSidebar div[data-baseweb="popover"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
}

.stSidebar div[data-baseweb="popover"] div {
    background: #1e293b !important;
    color: #e2e8f0 !important;
}

.stSidebar div[data-baseweb="popover"] div:hover {
    background: #334155 !important;
}

/* Filter spacing */
.stSidebar > div > div > div {
    margin-bottom: 24px !important;
}

.stSidebar > div > div > div:last-child {
    margin-bottom: 0 !important;
}

/* Ultra-aggressive metric text fixes */
.stColumn div[data-testid="metric-container"] label,
.stColumn div[data-testid="metric-container"] span,
.stColumn div[data-testid="metric-container"] p,
.stColumn div[data-testid="metric-container"] div,
.stColumn [data-testid="metric-container"] label,
.stColumn [data-testid="metric-container"] span,
.stColumn [data-testid="metric-container"] p,
.stColumn [data-testid="metric-container"] div {
    color: #ffffff !important;
    font-weight: 700 !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8) !important;
}

/* Target by data attributes and CSS classes */
div[data-testid="metric-container"] * {
    color: #ffffff !important;
}

/* Override any inherited styles */
.stColumn > div * {
    color: #ffffff !important;
}

/* Force override all text in metric columns */
.stColumn div,
.stColumn span,
.stColumn p,
.stColumn label {
    color: #ffffff !important;
}

/* TARGETED FIX: Hide only empty first child elements */
.main .block-container > div:first-child:empty {
    display: none !important;
}

/* Hide first child only if it doesn't contain important content */
.main .block-container > div:first-child:not(:has(h1)):not(:has([data-testid="stTitle"])):not(:has(.stMetric)) {
    display: none !important;
}

/* Make sure title appears properly styled */
.main h1, .stTitle h1, h1 {
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    text-align: center !important;
    margin-bottom: 2rem !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}

/* Force all Streamlit titles to be white */
[data-testid="stTitle"] h1,
[data-testid="stHeader"] h1,
.main .stTitle h1 {
    color: #ffffff !important;
}

/* ULTRA AGGRESSIVE: Hide ALL empty containers in chat tab */
[data-baseweb="tab-panel"] > div,
[data-baseweb="tab-panel"] .element-container,
[data-baseweb="tab-panel"] .stVerticalBlock > div,
[data-baseweb="tab-panel"] [data-testid="element-container"],
[data-baseweb="tab-panel"] [data-testid="stVerticalBlock"],
[data-baseweb="tab-panel"] .stColumn > div {
    margin: 0 !important;
    padding: 0 !important;
}

/* Hide empty containers completely */
[data-baseweb="tab-panel"] > div:empty,
[data-baseweb="tab-panel"] .element-container:empty,
[data-baseweb="tab-panel"] .stVerticalBlock > div:empty,
[data-baseweb="tab-panel"] [data-testid="element-container"]:empty,
[data-baseweb="tab-panel"] [data-testid="stVerticalBlock"]:empty,
[data-baseweb="tab-panel"] .stColumn > div:empty,
[data-baseweb="tab-panel"] .stMarkdown:empty {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    max-height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    opacity: 0 !important;
}

/* Hide containers that only have whitespace */
[data-baseweb="tab-panel"] > div:not(:has(*:not(:empty))),
[data-baseweb="tab-panel"] .element-container:not(:has(*:not(:empty))),
[data-baseweb="tab-panel"] [data-testid="element-container"]:not(:has(*:not(:empty))) {
    display: none !important;
}

/* Aggressively target empty divs in chat section */
[data-baseweb="tab-panel"] div:not([class]):empty,
[data-baseweb="tab-panel"] div[class=""]:empty,
[data-baseweb="tab-panel"] div:not(:has(input)):not(:has(button)):not(:has(.chat-message)):not(:has(.chat-container)):empty {
    display: none !important;
}

/* Remove spacing from containers that don't have important content */
[data-baseweb="tab-panel"] > div:not(:has(input)):not(:has(button)):not(:has(.chat-message)):not(:has(.chat-container)):not(:has(.modern-chat-input)):not(:has(.compact-actions)) {
    margin: 0 !important;
    padding: 0 !important;
    min-height: 0 !important;
}

/* Target the specific empty boxes we see in the screenshot */
[data-baseweb="tab-panel"] > .element-container:not(:has(.chat-container)):not(:has(.modern-chat-input)):not(:has(form)) {
    display: none !important;
}

/* Hide any div that doesn't contain essential chat elements */
[data-baseweb="tab-panel"] > div:not(:has(.section-header)):not(:has(.chat-container)):not(:has(.modern-chat-input)):not(:has(form)):not(:has(.compact-actions)):not(:has(button)):not(:has(input)) {
    display: none !important;
}

/* Chat interface styling - No background container */
.chat-container {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    max-height: 400px;
    overflow-y: auto;
}

.chat-message {
    background: rgba(51, 65, 85, 0.5) !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin: 4px 0 !important;
    color: #f1f5f9 !important;
    border-left: 2px solid #667eea !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.15s ease !important;
    font-size: 13px !important;
    line-height: 1.4 !important;
}

.chat-message:hover {
    transform: translateX(2px) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}

.chat-message.user {
    background: rgba(67, 233, 123, 0.15) !important;
    border-left: 2px solid #43e97b !important;
    margin-left: 20px !important;
    color: #e2e8f0 !important;
}

.chat-message.assistant {
    background: rgba(102, 126, 234, 0.15) !important;
    border-left: 2px solid #667eea !important;
    margin-right: 20px !important;
    color: #e2e8f0 !important;
}

.chat-input-container {
    background: linear-gradient(135deg, #334155 0%, #475569 100%) !important;
    border-radius: 20px !important;
    padding: 4px !important;
    border: 2px solid transparent !important;
    background-clip: padding-box !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
}

.chat-input-container:hover {
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.3) !important;
    border-color: #667eea !important;
}

.chat-input-container:focus-within {
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4) !important;
    border-color: #667eea !important;
}

/* Modern compact chat input */
.modern-chat-input {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    padding: 6px !important;
    margin: 8px 0 !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.15s ease !important;
}

.modern-chat-input:hover {
    border-color: #475569 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
}

.modern-chat-input:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1), 0 2px 6px rgba(0, 0, 0, 0.15) !important;
}

/* Compact actions */
.compact-actions {
    display: flex !important;
    gap: 6px !important;
    align-items: center !important;
    margin: 6px 0 !important;
}

.compact-actions .stButton > button {
    background: rgba(51, 65, 85, 0.4) !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
    color: #94a3b8 !important;
    padding: 4px !important;
    min-height: 28px !important;
    width: 28px !important;
    font-size: 12px !important;
    transition: all 0.15s ease !important;
}

.compact-actions .stButton > button:hover {
    background: rgba(71, 85, 105, 0.6) !important;
    color: #e2e8f0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2) !important;
}

/* Modern compact text input styling */
.modern-chat-input .stTextInput > div > div > input {
    background: transparent !important;
    border: none !important;
    color: #f1f5f9 !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    outline: none !important;
    box-shadow: none !important;
    width: 100% !important;
}

.modern-chat-input .stTextInput > div > div > input::placeholder {
    color: #64748b !important;
    font-weight: 400 !important;
    opacity: 1 !important;
}

.modern-chat-input .stTextInput > div > div > input:focus {
    background: rgba(30, 41, 59, 0.3) !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #ffffff !important;
}

.modern-chat-input .stTextInput > div > div {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
}

.modern-chat-input .stTextInput {
    background: transparent !important;
}

.stTextInput > div > div > input::placeholder {
    color: #94a3b8 !important;
    font-weight: 400 !important;
    opacity: 1 !important;
}

.stTextInput > div > div > input:focus {
    background: rgba(30, 41, 59, 0.9) !important;
    border: 1px solid #667eea !important;
    outline: none !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1), 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    color: #ffffff !important;
}

.stTextInput > div > div {
    background: transparent !important;
    border: none !important;
    border-radius: 16px !important;
}

.stTextInput {
    background: transparent !important;
}

/* Additional input field overrides for better visibility */
.chat-input-container .stTextInput > div > div > input {
    background: rgba(30, 41, 59, 0.9) !important;
    color: #ffffff !important;
    border: 2px solid #475569 !important;
}

.chat-input-container .stTextInput > div > div > input:focus {
    border: 2px solid #667eea !important;
    color: #ffffff !important;
    background: rgba(30, 41, 59, 1) !important;
}

/* Send button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: 2px solid #667eea !important;
    border-radius: 16px !important;
    color: #ffffff !important;
    padding: 16px 32px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4) !important;
    min-height: 56px !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.6) !important;
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    border-color: #764ba2 !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4) !important;
}

/* Modern compact send button */
.modern-chat-input .stButton > button,
.modern-chat-input button[kind="formSubmit"],
.modern-chat-input [data-testid="stFormSubmitButton"] > button,
.modern-chat-input form[data-testid="stForm"] .stButton > button {
    background: #667eea !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 8px !important;
    border-radius: 6px !important;
    min-height: 32px !important;
    width: 32px !important;
    box-shadow: 0 1px 4px rgba(102, 126, 234, 0.3) !important;
    text-shadow: none !important;
    opacity: 1 !important;
    visibility: visible !important;
    transition: all 0.15s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Modern send button hover */
.modern-chat-input .stButton > button:hover,
.modern-chat-input button[kind="formSubmit"]:hover,
.modern-chat-input [data-testid="stFormSubmitButton"] > button:hover,
.modern-chat-input form[data-testid="stForm"] .stButton > button:hover {
    background: #5a67d8 !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    transform: translateY(-1px) !important;
}

.modern-chat-input .stButton > button:active,
.modern-chat-input button[kind="formSubmit"]:active,
.modern-chat-input [data-testid="stFormSubmitButton"] > button:active,
.modern-chat-input form[data-testid="stForm"] .stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
}

/* Additional targeting for form submit buttons */
[data-testid="stForm"] button {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
    border: 2px solid #43e97b !important;
    color: #0f172a !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 16px rgba(67, 233, 123, 0.4) !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Force all buttons in chat container to be visible */
.chat-input-container button {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
    border: 2px solid #43e97b !important;
    color: #0f172a !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 16px rgba(67, 233, 123, 0.4) !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Clear button styling */
.stButton:last-child > button {
    background: linear-gradient(135deg, #64748b 0%, #475569 100%) !important;
    color: #f1f5f9 !important;
    box-shadow: 0 4px 16px rgba(100, 116, 139, 0.2) !important;
    margin-top: 16px !important;
}

.stButton:last-child > button:hover {
    background: linear-gradient(135deg, #475569 0%, #334155 100%) !important;
    box-shadow: 0 8px 24px rgba(100, 116, 139, 0.3) !important;
}
</style>

<script>
// Aggressively clean up empty containers
function cleanupEmptyContainers() {
    // Remove empty containers in chat tab
    const chatTabPanel = document.querySelector('[data-baseweb="tab-panel"]:has(.section-header)');
    if (chatTabPanel) {
        // Find all direct children that are empty or only contain whitespace
        const children = Array.from(chatTabPanel.children);
        children.forEach(child => {
            if (!child.textContent.trim() && 
                !child.querySelector('input') && 
                !child.querySelector('button') && 
                !child.querySelector('form') &&
                !child.classList.contains('chat-container') &&
                !child.classList.contains('modern-chat-input') &&
                !child.classList.contains('compact-actions') &&
                !child.querySelector('.section-header')) {
                child.style.display = 'none';
                child.style.visibility = 'hidden';
                child.style.height = '0';
                child.style.margin = '0';
                child.style.padding = '0';
            }
        });
        
        // Also target element containers specifically
        const elementContainers = chatTabPanel.querySelectorAll('[data-testid="element-container"]');
        elementContainers.forEach(container => {
            if (!container.textContent.trim() && 
                !container.querySelector('input') && 
                !container.querySelector('button') && 
                !container.querySelector('form')) {
                container.style.display = 'none';
            }
        });
    }
    
    // Remove empty containers at the top
    const containers = document.querySelectorAll('.main .block-container > div');
    if (containers.length > 0) {
        const firstContainer = containers[0];
        if (!firstContainer.querySelector('h1') && !firstContainer.querySelector('[data-testid="metric-container"]')) {
            firstContainer.style.display = 'none';
        }
    }
}

// Run cleanup on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(cleanupEmptyContainers, 200);
    setTimeout(cleanupEmptyContainers, 500);
    setTimeout(cleanupEmptyContainers, 1000);
});

// Use MutationObserver to catch dynamically added empty containers
const observer = new MutationObserver(function(mutations) {
    let shouldCleanup = false;
    mutations.forEach(mutation => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            shouldCleanup = true;
        }
    });
    if (shouldCleanup) {
        setTimeout(cleanupEmptyContainers, 100);
    }
});

// Start observing when DOM is ready
if (document.querySelector('.main')) {
    observer.observe(document.querySelector('.main'), {
        childList: true,
        subtree: true
    });
}

// Enhance sidebar toggle functionality
function enhanceSidebarToggle() {
    const toggleButton = document.querySelector('button[data-testid="collapsedControl"]');
    if (toggleButton) {
        // Ensure button is always visible and styled
        toggleButton.style.display = 'flex';
        toggleButton.style.alignItems = 'center';
        toggleButton.style.justifyContent = 'center';
        toggleButton.style.visibility = 'visible';
        toggleButton.style.opacity = '1';
        
        // Add tooltip
        toggleButton.title = 'Toggle Filters Panel';
        
        // Add custom icon if not present
        if (!toggleButton.textContent.includes('🎛️')) {
            toggleButton.innerHTML = '<span style="font-size: 20px;">🎛️</span>';
        }
    }
}

// Run sidebar enhancement
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(enhanceSidebarToggle, 500);
    setTimeout(enhanceSidebarToggle, 1000);
    setTimeout(enhanceSidebarToggle, 2000);
});

// Also run on any DOM changes
const sidebarObserver = new MutationObserver(function(mutations) {
    enhanceSidebarToggle();
});

if (document.body) {
    sidebarObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
}
</script>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load processed conversation data"""
    try:
        conversations_df = pd.read_csv('data/processed_conversations.csv')
        daily_df = pd.read_csv('data/daily_aggregations.csv')
        
        # Convert date columns
        conversations_df['start_date'] = pd.to_datetime(conversations_df['start_date'])
        conversations_df['end_date'] = pd.to_datetime(conversations_df['end_date'])
        daily_df['date'] = pd.to_datetime(daily_df['date'])
        
        return conversations_df, daily_df
    except FileNotFoundError:
        st.error("Data files not found. Please run data_processor.py first.")
        return None, None

def create_dark_template():
    """Create dark theme template for Plotly charts"""
    return {
        'layout': {
            'paper_bgcolor': '#1e293b',
            'plot_bgcolor': '#1e293b',
            'font': {
                'family': 'Inter, sans-serif',
                'color': '#e2e8f0'
            },
            'colorway': ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#764ba2', '#f5576c'],
            'margin': {'l': 20, 'r': 20, 't': 40, 'b': 20},
            'xaxis': {
                'gridcolor': '#334155',
                'zerolinecolor': '#475569',
                'tickcolor': '#64748b',
                'linecolor': '#475569'
            },
            'yaxis': {
                'gridcolor': '#334155',
                'zerolinecolor': '#475569',
                'tickcolor': '#64748b',
                'linecolor': '#475569'
            },
            'legend': {
                'bgcolor': 'rgba(30, 41, 59, 0.8)',
                'bordercolor': '#475569',
                'font': {'color': '#e2e8f0'}
            }
        }
    }

def send_chat_message(message, conversation_history):
    """Send message to the chat API"""
    api_url = "https://76wnfi088i.execute-api.us-west-2.amazonaws.com/PROD/chat"
    
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }
    
    # Generate a unique session ID for this chat session
    import uuid
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # Prepare the payload in the correct format
    body_content = {
        "input": message,
        "sessionId": st.session_state.session_id
    }
    
    payload = {
        "body": json.dumps(body_content)
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Handle the response format
            if "body" in response_data:
                # Parse the body if it's a string
                body = json.loads(response_data["body"]) if isinstance(response_data["body"], str) else response_data["body"]
                
                # Look for the response content in various possible fields
                if "response" in body:
                    return body["response"]
                elif "output" in body:
                    return body["output"]
                elif "message" in body:
                    return body["message"]
                elif "content" in body:
                    if isinstance(body["content"], list) and len(body["content"]) > 0:
                        return body["content"][0].get("text", str(body["content"][0]))
                    return str(body["content"])
                else:
                    # Return the entire body if we can't find a specific field
                    return str(body)
            elif "response" in response_data:
                return response_data["response"]
            elif "message" in response_data:
                return response_data["message"]
            else:
                return f"Received response: {str(response_data)}"
        else:
            error_text = response.text
            return f"API Error {response.status_code}: {error_text}"
    except requests.exceptions.RequestException as e:
        return f"Connection Error: {str(e)}"
    except json.JSONDecodeError as e:
        return f"JSON Error: {str(e)}"
    except Exception as e:
        return f"Processing Error: {str(e)}"

def main():
    # Load data
    conversations_df, daily_df = load_data()
    
    if conversations_df is None:
        return
    
    # No title - KPIs should appear first
    
    # Sidebar filters
    with st.sidebar:
        st.markdown('<div class="section-header">🎛️ Filters</div>', unsafe_allow_html=True)
        
        # Date range filter
        min_date = conversations_df['start_date'].min().date()
        max_date = conversations_df['start_date'].max().date()
        
        date_range = st.date_input(
            "Date Range",
            value=(max_date - timedelta(days=30), max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Agent filter
        agent_list = ['All'] + sorted(conversations_df['agent_name'].unique().tolist())
        selected_agents = st.multiselect(
            "Select Agents",
            agent_list,
            default=['All']
        )
        
        # Topic filter
        topic_list = ['All'] + sorted(conversations_df['primary_topic'].unique().tolist())
        selected_topics = st.multiselect(
            "Select Topics",
            topic_list,
            default=['All']
        )
        
        # Sentiment range
        sentiment_range = st.slider(
            "Sentiment Range",
            -1.0, 1.0, (-1.0, 1.0),
            step=0.1
        )
        
        # Outcome filter
        outcome_options = ['All', 'successful', 'unsuccessful', 'escalated']
        selected_outcome = st.selectbox(
            "Outcome Filter",
            outcome_options
        )
    
    # Filter data based on selections
    filtered_df = conversations_df.copy()
    
    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['start_date'].dt.date >= start_date) & 
            (filtered_df['start_date'].dt.date <= end_date)
        ]
    
    if 'All' not in selected_agents and selected_agents:
        filtered_df = filtered_df[filtered_df['agent_name'].isin(selected_agents)]
    
    if 'All' not in selected_topics and selected_topics:
        filtered_df = filtered_df[filtered_df['primary_topic'].isin(selected_topics)]
    
    filtered_df = filtered_df[
        (filtered_df['sentiment_score'] >= sentiment_range[0]) & 
        (filtered_df['sentiment_score'] <= sentiment_range[1])
    ]
    
    if selected_outcome != 'All':
        filtered_df = filtered_df[filtered_df['outcome'] == selected_outcome]
    
    # Key Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    
    total_conversations = len(filtered_df)
    success_rate = (len(filtered_df[filtered_df['outcome'] == 'successful']) / total_conversations * 100) if total_conversations > 0 else 0
    avg_sentiment = filtered_df['sentiment_score'].mean() if total_conversations > 0 else 0
    avg_empathy = filtered_df['empathy_score'].mean() if total_conversations > 0 else 0
    
    with col1:
        st.metric("Total Conversations", f"{total_conversations:,}", delta="+5.2%")
    
    with col2:
        st.metric("Success Rate", f"{success_rate:.1f}%", delta="+2.3%")
    
    with col3:
        st.metric("Avg. Sentiment", f"{(avg_sentiment + 1) * 5:.1f}/10", delta="+0.5")
    
    with col4:
        st.metric("Avg. Empathy", f"{avg_empathy * 10:.1f}/10", delta="+0.3")
    
    # Main content in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Outcomes", "🏷️ Topics", "😊 Sentiment", "📋 Insights", "💬 Chat"])
    
    # Dark template for charts
    dark_template = create_dark_template()
    
    with tab1:
        st.markdown('<div class="section-header">Conversation Outcomes</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Donut chart for outcomes
            outcome_counts = filtered_df['outcome'].value_counts()
            fig_donut = go.Figure(data=[go.Pie(
                labels=outcome_counts.index,
                values=outcome_counts.values,
                hole=.3
            )])
            fig_donut.update_layout(
                title="Conversation Outcomes Distribution",
                **dark_template['layout']
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        
        with col2:
            # Success rate by agent
            agent_success = filtered_df.groupby('agent_name').agg({
                'outcome': lambda x: (x == 'successful').mean() * 100
            }).reset_index()
            agent_success.columns = ['agent_name', 'success_rate']
            
            fig_agent = px.bar(
                agent_success.sort_values('success_rate', ascending=True),
                x='success_rate',
                y='agent_name',
                orientation='h',
                title="Success Rate by Agent"
            )
            fig_agent.update_layout(**dark_template['layout'])
            st.plotly_chart(fig_agent, use_container_width=True)
        
        # Success rate trend
        daily_success = filtered_df.groupby(filtered_df['start_date'].dt.date).agg({
            'outcome': lambda x: (x == 'successful').mean() * 100
        }).reset_index()
        daily_success.columns = ['date', 'success_rate']
        
        fig_trend = px.line(
            daily_success,
            x='date',
            y='success_rate',
            title="Success Rate Trend Over Time"
        )
        fig_trend.update_layout(**dark_template['layout'])
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-header">Topic Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top topics by frequency
            topic_counts = filtered_df['primary_topic'].value_counts().head(10)
            fig_topics = px.bar(
                x=topic_counts.values,
                y=topic_counts.index,
                orientation='h',
                title="Top 10 Topics by Frequency"
            )
            fig_topics.update_layout(**dark_template['layout'])
            st.plotly_chart(fig_topics, use_container_width=True)
        
        with col2:
            # Topics by outcome
            topic_outcome = pd.crosstab(filtered_df['primary_topic'], filtered_df['outcome'])
            fig_topic_outcome = px.bar(
                topic_outcome.reset_index(),
                x='primary_topic',
                y=['successful', 'unsuccessful', 'escalated'],
                title="Topics by Outcome",
                barmode='group'
            )
            fig_topic_outcome.update_layout(**dark_template['layout'])
            fig_topic_outcome.update_layout(xaxis={'tickangle': 45})
            st.plotly_chart(fig_topic_outcome, use_container_width=True)
        
        # Topic performance table
        topic_performance = filtered_df.groupby('primary_topic').agg({
            'conversation_id': 'count',
            'outcome': lambda x: (x == 'successful').mean() * 100,
            'sentiment_score': 'mean',
            'empathy_score': 'mean'
        }).reset_index()
        
        topic_performance.columns = ['Topic', 'Count', 'Success Rate (%)', 'Avg Sentiment', 'Avg Empathy']
        topic_performance['Success Rate (%)'] = topic_performance['Success Rate (%)'].round(1)
        topic_performance['Avg Sentiment'] = topic_performance['Avg Sentiment'].round(2)
        topic_performance['Avg Empathy'] = topic_performance['Avg Empathy'].round(2)
        
        st.markdown('<div class="section-header">Topic Performance Summary</div>', unsafe_allow_html=True)
        st.dataframe(topic_performance, use_container_width=True)
    
    with tab3:
        st.markdown('<div class="section-header">Sentiment & Empathy Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment gauge
            avg_sentiment_normalized = (avg_sentiment + 1) * 50  # Convert to 0-100 scale
            fig_sentiment_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = avg_sentiment_normalized,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Sentiment Score"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#667eea"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 100], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_sentiment_gauge.update_layout(**dark_template['layout'])
            st.plotly_chart(fig_sentiment_gauge, use_container_width=True)
        
        with col2:
            # Empathy gauge
            avg_empathy_normalized = avg_empathy * 100
            fig_empathy_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = avg_empathy_normalized,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Empathy Score"},
                delta = {'reference': 80},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#764ba2"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 100], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_empathy_gauge.update_layout(**dark_template['layout'])
            st.plotly_chart(fig_empathy_gauge, use_container_width=True)
        
        # Sentiment vs Empathy scatter
        fig_scatter = px.scatter(
            filtered_df,
            x='sentiment_score',
            y='empathy_score',
            color='outcome',
            title="Sentiment vs Empathy Correlation",
            hover_data=['primary_topic', 'agent_name']
        )
        fig_scatter.update_layout(**dark_template['layout'])
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Sentiment by topic boxplot
        fig_box = px.box(
            filtered_df,
            x='primary_topic',
            y='sentiment_score',
            title="Sentiment Distribution by Topic"
        )
        fig_box.update_layout(**dark_template['layout'])
        fig_box.update_layout(xaxis={'tickangle': 45})
        st.plotly_chart(fig_box, use_container_width=True)
    
    with tab4:
        st.markdown('<div class="section-header">Detailed Insights</div>', unsafe_allow_html=True)
        
        # Key insights
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: white; margin-bottom: 1rem;">📊 Key Insights</h3>
            <ul style="color: rgba(255, 255, 255, 0.9); line-height: 1.6;">
                <li><strong>Top Performing Topic:</strong> {}</li>
                <li><strong>Most Challenging Topic:</strong> {}</li>
                <li><strong>Best Performing Agent:</strong> {}</li>
                <li><strong>Average Resolution Time:</strong> {:.1f} minutes</li>
            </ul>
        </div>
        """.format(
            topic_performance.loc[topic_performance['Success Rate (%)'].idxmax(), 'Topic'],
            topic_performance.loc[topic_performance['Success Rate (%)'].idxmin(), 'Topic'],
            agent_success.loc[agent_success['success_rate'].idxmax(), 'agent_name'],
            filtered_df['duration_minutes'].mean()
        ), unsafe_allow_html=True)
        
        # Recent conversations table
        st.markdown('<div class="section-header">Recent Conversations</div>', unsafe_allow_html=True)
        recent_conversations = filtered_df.nlargest(10, 'start_date')[
            ['start_date', 'agent_name', 'primary_topic', 'outcome', 'sentiment_score', 'duration_minutes']
        ].copy()
        recent_conversations['start_date'] = recent_conversations['start_date'].dt.strftime('%Y-%m-%d %H:%M')
        recent_conversations['sentiment_score'] = recent_conversations['sentiment_score'].round(2)
        recent_conversations['duration_minutes'] = recent_conversations['duration_minutes'].round(1)
        
        st.dataframe(recent_conversations, use_container_width=True)
    
    with tab5:
        st.markdown('<div class="section-header">💬 Interactive Chat Assistant</div>', unsafe_allow_html=True)
        
        # Initialize chat history in session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Display chat history
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    st.markdown(f'''
                    <div class="chat-message user">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="font-size: 11px; opacity: 0.7;">👤</span>
                            <strong style="font-size: 12px;">You</strong>
                        </div>
                        <div style="margin-top: 2px;">{message["content"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="chat-message assistant">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="font-size: 11px; opacity: 0.7;">🤖</span>
                            <strong style="font-size: 12px;">Assistant</strong>
                        </div>
                        <div style="margin-top: 2px;">{message["content"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Check if we need to get API response (if last message is "thinking...")
        if (st.session_state.chat_history and 
            st.session_state.chat_history[-1]["role"] == "assistant" and 
            st.session_state.chat_history[-1]["content"] == "🤔 Thinking..."):
            
            # Get the user message (second to last)
            user_message = st.session_state.chat_history[-2]["content"]
            
            # Get AI response
            ai_response = send_chat_message(user_message, st.session_state.chat_history[:-2])
            
            # Replace the thinking message with actual response
            st.session_state.chat_history[-1] = {
                "role": "assistant",
                "content": ai_response
            }
            
            # Rerun to show the actual response
            st.rerun()
        
        # Modern compact chat input
        st.markdown('<div class="modern-chat-input">', unsafe_allow_html=True)
        
        # Compact single-line form
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([6, 1])
            
            with col1:
                user_input = st.text_input(
                    "Chat Input",
                    key="chat_input", 
                    placeholder="Ask about your analytics...",
                    label_visibility="collapsed",
                    help="Press Enter or click Send"
                )
            
            with col2:
                send_button = st.form_submit_button("↗", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Compact action row
        if st.session_state.chat_history:
            st.markdown('<div class="compact-actions">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 1, 4])
            
            with col1:
                if st.button("🗑", key="clear_chat_compact", help="Clear chat"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("📋", key="export_chat_compact", help="Export chat"):
                    st.success("Export coming soon!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle message sending
        if send_button and user_input.strip():
            # Add user message to history immediately
            st.session_state.chat_history.append({
                "role": "user", 
                "content": user_input
            })
            
            # Add temporary "thinking..." message
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "🤔 Thinking..."
            })
            
            # Rerun to show user message and thinking indicator
            st.rerun()
        
        # Quick action suggestions - Compact version
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="margin-top: 12px;">
                <div style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;">
                    <div style="background: rgba(102, 126, 234, 0.1); border: 1px solid rgba(102, 126, 234, 0.2); border-radius: 8px; padding: 6px 10px; font-size: 12px; color: #94a3b8;">
                        💡 "What's my highest performing agent?"
                    </div>
                    <div style="background: rgba(67, 233, 123, 0.1); border: 1px solid rgba(67, 233, 123, 0.2); border-radius: 8px; padding: 6px 10px; font-size: 12px; color: #94a3b8;">
                        📈 "Show me sentiment trends"
                    </div>
                    <div style="background: rgba(240, 147, 251, 0.1); border: 1px solid rgba(240, 147, 251, 0.2); border-radius: 8px; padding: 6px 10px; font-size: 12px; color: #94a3b8;">
                        🎯 "How can I improve success rates?"
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()