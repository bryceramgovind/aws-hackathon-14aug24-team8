# Streamlit Customer Contact Centre Analysis Dashboard Design

## Dashboard Overview
A comprehensive analytics dashboard for customer contact center conversations with real-time insights into conversation outcomes, topics, sentiment, and agent performance.

## Proposed Dashboard Layout

### 1. **Header Section**
- Title: "Customer Contact Centre Analytics Dashboard"
- Date range selector (default: last 30 days)
- Refresh button
- Export options (PDF/CSV)

### 2. **Key Metrics Cards (Top Row)**
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Total           │ Success Rate    │ Avg. Sentiment  │ Avg. Empathy    │
│ Conversations   │                 │ Score           │ Score           │
│ 12,456          │ 78.5%           │ 7.2/10          │ 8.1/10          │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### 3. **Main Analytics Sections**

#### Section A: Conversation Outcomes
- **Chart 1**: Donut Chart - Success vs Unsuccessful Conversations
- **Chart 2**: Line Chart - Success Rate Trend (Daily/Weekly/Monthly)
- **Chart 3**: Bar Chart - Success Rate by Agent

#### Section B: Topic Analysis
- **Chart 4**: Horizontal Bar Chart - Top 10 Topics by Frequency
- **Chart 5**: Grouped Bar Chart - Topics by Outcome (Success/Failure)
- **Chart 6**: Word Cloud - Most Common Keywords
- **Chart 7**: Treemap - Topic Hierarchy and Volume

#### Section C: Sentiment & Empathy Analysis
- **Chart 8**: Gauge Charts - Overall Sentiment & Empathy Scores
- **Chart 9**: Scatter Plot - Sentiment vs Empathy Correlation
- **Chart 10**: Box Plot - Sentiment Distribution by Topic
- **Chart 11**: Heatmap - Topic vs Sentiment Matrix

#### Section D: Detailed Insights
- **Table 1**: Topic Performance Summary
  - Columns: Topic, Count, Success Rate, Avg Sentiment, Avg Empathy
- **Chart 12**: Stacked Area Chart - Sentiment Trend by Topic Over Time

### 4. **Sidebar Filters**
- Agent selection (multi-select)
- Topic filter (multi-select)
- Sentiment range slider
- Outcome filter (Success/Failure/All)
- Customer type filter

## Enhanced Data Schema Recommendations

### 1. **Conversation Summary Table**
```json
{
    "conversation_id": "string",
    "contact_id": "string",
    "start_date": "timestamp",
    "end_date": "timestamp",
    "duration_minutes": "float",
    "agent_id": "string",
    "agent_name": "string",
    "customer_id": "string",
    "outcome": "string", // "successful", "unsuccessful", "escalated"
    "outcome_confidence": "float", // 0-1
    "primary_topic": "string",
    "secondary_topics": ["array of strings"],
    "sentiment_score": "float", // -1 to 1
    "empathy_score": "float", // 0 to 1
    "message_count": "integer",
    "resolution_time_minutes": "float"
}
```

### 2. **Message Analytics Table**
```json
{
    "message_id": "string",
    "conversation_id": "string",
    "message_number": "integer",
    "user_type": "string", // "customer", "agent"
    "message_text": "string",
    "timestamp": "timestamp",
    "sentiment_score": "float",
    "empathy_score": "float", // only for agent messages
    "detected_topics": ["array of strings"],
    "intent": "string",
    "emotion": "string" // "happy", "frustrated", "neutral", etc.
}
```

### 3. **Topic Analytics Table**
```json
{
    "topic_id": "string",
    "topic_name": "string",
    "topic_category": "string",
    "parent_topic": "string", // for hierarchical topics
    "keywords": ["array of strings"],
    "typical_resolution_time": "float",
    "complexity_score": "float" // 1-5
}
```

### 4. **Daily Aggregations Table**
```json
{
    "date": "date",
    "total_conversations": "integer",
    "successful_conversations": "integer",
    "avg_sentiment": "float",
    "avg_empathy": "float",
    "top_topics": ["array of strings"],
    "avg_duration": "float"
}
```

## RAG Implementation Options

### 1. **Conversation Insights RAG**
- **Purpose**: Generate natural language insights from conversation data
- **Implementation**:
  ```python
  # Vector store for conversation embeddings
  - Embed full conversations
  - Store with metadata (outcome, sentiment, topics)
  - Query: "Show me examples of successful roaming conversations"
  ```

### 2. **Best Practice Recommendations RAG**
- **Purpose**: Suggest improvements based on successful conversations
- **Implementation**:
  ```python
  # Index successful conversation patterns
  - Extract winning phrases and approaches
  - Generate recommendations for specific topics
  - Query: "How should agents handle billing complaints?"
  ```

### 3. **Interactive Q&A Interface**
- **Features**:
  - Natural language queries about data
  - Conversation examples retrieval
  - Trend explanations
  - Suggested actions

### 4. **RAG-Enhanced Features in Dashboard**:
```
┌─────────────────────────────────────────────────────┐
│ 💬 Ask Analytics Assistant                          │
│ ┌─────────────────────────────────────────────────┐ │
│ │ "What are the main reasons for failed           │ │
│ │  conversations about roaming?"                   │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ 📊 Insights:                                        │
│ • 45% fail due to pricing confusion                │
│ • 30% due to technical setup issues                │
│ • Successful agents use step-by-step guidance      │
│                                                     │
│ 💡 Recommendations:                                 │
│ • Create visual roaming setup guide                │
│ • Standardize pricing explanation                  │
└─────────────────────────────────────────────────────┘
```

## Streamlit Implementation Structure

```python
# main.py structure
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Contact Centre Analytics",
    page_icon="📊",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now())
    )
    selected_agents = st.multiselect("Select Agents", agent_list)
    selected_topics = st.multiselect("Select Topics", topic_list)
    sentiment_range = st.slider("Sentiment Range", -1.0, 1.0, (-1.0, 1.0))

# Main dashboard
st.title("Customer Contact Centre Analytics Dashboard")

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Conversations", "12,456", "+5.2%")
with col2:
    st.metric("Success Rate", "78.5%", "+2.3%")
with col3:
    st.metric("Avg. Sentiment", "7.2/10", "+0.5")
with col4:
    st.metric("Avg. Empathy", "8.1/10", "+0.3")

# Tabbed sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Outcomes", "Topics", "Sentiment", "Insights", "AI Assistant"
])
```

## Key Features to Implement

1. **Real-time Updates**: Use Streamlit's auto-refresh capability
2. **Drill-down Capability**: Click on charts to see conversation details
3. **Export Functionality**: Download filtered data and reports
4. **Alerting System**: Highlight concerning trends
5. **Comparison Mode**: Compare different time periods or agent groups
6. **Mobile Responsive**: Ensure dashboard works on tablets for supervisors

This design provides a comprehensive view of contact center performance while maintaining usability and actionable insights.