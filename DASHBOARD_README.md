# Customer Contact Centre Analytics Dashboard

A comprehensive, modern analytics dashboard for customer contact center conversations featuring glassmorphism and neumorphic design elements built with Streamlit.

## 🌟 Features

### Dashboard Highlights
- **Modern UI Design**: Glassmorphism and neumorphic styling for a premium user experience
- **Real-time Analytics**: Key metrics including conversation volume, success rates, sentiment, and empathy scores
- **Interactive Visualizations**: Multiple chart types powered by Plotly with glass-themed styling
- **Advanced Filtering**: Dynamic filters for agents, topics, sentiment ranges, and outcomes
- **Multi-tab Navigation**: Organized sections for outcomes, topics, sentiment analysis, and detailed insights

### Key Metrics Displayed
- Total Conversations with growth indicators
- Success Rate with trending
- Average Sentiment Score (0-10 scale)
- Average Empathy Score (0-10 scale)

### Analytics Sections

#### 📈 Conversation Outcomes
- Donut chart showing success vs unsuccessful vs escalated conversations
- Success rate by agent horizontal bar chart
- Success rate trend over time line chart

#### 🏷️ Topic Analysis
- Top 10 topics by frequency horizontal bar chart
- Topics by outcome grouped bar chart
- Topic performance summary table with success rates, sentiment, and empathy scores

#### 😊 Sentiment & Empathy Analysis
- Gauge charts for overall sentiment and empathy scores
- Sentiment vs empathy correlation scatter plot
- Sentiment distribution by topic box plot

#### 📋 Detailed Insights
- Key insights summary with glassmorphism cards
- Recent conversations table
- Performance highlights

## 🚀 Quick Start

### Option 1: Simple Script (Recommended)
```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

### Option 2: Python Launcher
```bash
python3 run_dashboard.py
```

### Option 3: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Process data (if needed)
python3 data_processor.py

# Launch dashboard
streamlit run dashboard.py --server.port 8501
```

The dashboard will be available at: http://localhost:8501

## 📁 Project Structure

```
├── dashboard.py              # Main Streamlit dashboard application
├── data_processor.py         # Data processing and analytics generation
├── run_dashboard.py          # Python launcher script
├── run_dashboard.sh          # Shell launcher script
├── requirements.txt          # Python dependencies
├── data/
│   ├── customer_service_chats.json    # Raw chat data
│   ├── processed_conversations.csv    # Processed conversation analytics
│   └── daily_aggregations.csv         # Daily aggregated metrics
├── design_guide.md           # Comprehensive design specifications
└── front_end_prompt.md       # Dashboard requirements and specifications
```

## 🎨 Design Features

### Glassmorphism Elements
- **Background**: Linear gradient (purple to blue)
- **Glass Cards**: Semi-transparent with backdrop blur and subtle borders
- **Hover Effects**: Smooth animations with enhanced shadows and background opacity
- **Typography**: Inter font family with optimized weight hierarchy

### Neumorphic Sidebar
- **Background**: Light gray with soft shadow insets
- **Filter Elements**: Raised appearance with dual-tone shadows
- **Interactive States**: Pressed effect on active selections

### Chart Styling
- **Transparent Backgrounds**: All charts use transparent backgrounds
- **Glass Color Palette**: Modern gradient colors matching the overall theme
- **Grid Lines**: Subtle white grid lines with low opacity
- **Responsive Design**: Charts adapt to container width

## 📊 Data Schema

### Processed Conversations
- **conversation_id**: Unique identifier
- **agent_name**: Agent handling the conversation
- **primary_topic**: Main topic category
- **outcome**: success/unsuccessful/escalated
- **sentiment_score**: -1 to 1 range
- **empathy_score**: 0 to 1 range
- **duration_minutes**: Conversation length

### Supported Topics
- Billing, Technical Support, Roaming, Account Management
- Cancellation, Service Issues, Data Usage, Payment
- International Plans, Device Support

## 🔧 Technical Requirements

### Dependencies
- streamlit >= 1.48.0
- pandas >= 2.3.0
- plotly >= 6.3.0
- numpy >= 2.3.0
- wordcloud >= 1.9.0
- seaborn >= 0.13.0
- matplotlib >= 3.10.0

### Browser Support
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

### Performance
- Optimized CSS with hardware acceleration
- Efficient data caching with Streamlit's @st.cache_data
- Responsive design for various screen sizes

## 🎛️ Configuration

### Customization Options
- **Port Configuration**: Modify port in run scripts (default: 8501)
- **Data Sources**: Update file paths in data_processor.py
- **Styling**: Modify CSS variables in dashboard.py
- **Chart Colors**: Adjust colorway in glass_template configuration

### Environment Variables
- No environment variables required for basic setup
- Optional: Set STREAMLIT_SERVER_PORT for custom port

## 📱 Usage Guide

### Filtering Data
1. **Date Range**: Select start and end dates using the date picker
2. **Agents**: Multi-select from available agents (default: All)
3. **Topics**: Multi-select from conversation topics (default: All)
4. **Sentiment Range**: Use slider to filter by sentiment scores
5. **Outcome Filter**: Choose specific outcomes or view all

### Navigation
- **Tabs**: Click on tab headers to switch between sections
- **Metrics**: Hover over metric cards to see enhanced styling
- **Charts**: Interactive Plotly charts with zoom, pan, and hover details
- **Tables**: Sortable and scrollable data tables

### Export Options
- **Screenshots**: Browser's built-in screenshot tools
- **Data Export**: Copy data from tables for external analysis
- **Charts**: Right-click on Plotly charts for export options

## 🔍 Analytics Insights

### Key Metrics Interpretation
- **Success Rate**: Percentage of conversations with successful outcomes
- **Sentiment Score**: Customer satisfaction indicator (-1 to 1, displayed as 0-10)
- **Empathy Score**: Agent empathy level (0 to 1, displayed as 0-10)
- **Duration**: Average conversation length in minutes

### Best Practices for Analysis
1. **Trend Analysis**: Use the success rate trend to identify patterns
2. **Agent Performance**: Compare agents using the success rate chart
3. **Topic Insights**: Identify challenging topics with low success rates
4. **Correlation**: Use sentiment vs empathy scatter plot to find optimization opportunities

## 🚧 Troubleshooting

### Common Issues
1. **Module Import Errors**: Run `pip install -r requirements.txt`
2. **Data Not Found**: Ensure `data_processor.py` has been executed
3. **Port Already in Use**: Change port in run scripts or stop existing processes
4. **Styling Issues**: Clear browser cache and refresh

### Performance Optimization
- **Large Datasets**: Consider data sampling for faster loading
- **Memory Usage**: Monitor system resources with large date ranges
- **Chart Rendering**: Reduce data points for complex visualizations

## 📈 Future Enhancements

### Planned Features
- Real-time data streaming capability
- Advanced AI-powered insights with RAG integration
- Custom dashboard layouts
- Export to PDF/Excel functionality
- Mobile-responsive improvements
- Custom alert system for threshold breaches

### Integration Possibilities
- AWS Bedrock for enhanced AI analytics
- Real-time chat data feeds
- Customer feedback integration
- Agent training recommendations
- Performance benchmarking

---

Built with ❤️ using Streamlit, Plotly, and modern web design principles.

For support or feature requests, please refer to the project documentation or create an issue in the repository.