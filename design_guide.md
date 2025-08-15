# Streamlit Dashboard Design Guide: Glassmorphism & Neumorphism

## Design Philosophy

This design guide establishes a modern, sophisticated visual identity for the Customer Contact Centre Analytics Dashboard using cutting-edge glassmorphism and neumorphism design trends. The approach creates an intuitive, premium user experience that enhances data visualization and usability.

## Color Palette

### Primary Colors
```css
/* Glassmorphism Base */
--glass-primary: rgba(255, 255, 255, 0.1)
--glass-secondary: rgba(255, 255, 255, 0.05)
--glass-accent: rgba(59, 130, 246, 0.3)

/* Neumorphism Base */
--neuro-bg: #f0f0f3
--neuro-light: #ffffff
--neuro-dark: #d1d1d4
--neuro-accent: #667eea

/* Text & Contrast */
--text-primary: #2d3748
--text-secondary: #718096
--text-accent: #4299e1
```

### Background Gradients
```css
/* Main Dashboard Background */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)

/* Glass Card Background */
background: rgba(255, 255, 255, 0.1)
backdrop-filter: blur(10px)
border: 1px solid rgba(255, 255, 255, 0.2)

/* Neuro Card Background */
background: #f0f0f3
box-shadow: 20px 20px 60px #d1d1d4, -20px -20px 60px #ffffff
```

## Typography

### Font Stack
```css
font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif
```

### Text Hierarchy
- **Dashboard Title**: 2.5rem, font-weight: 700, letter-spacing: -0.02em
- **Section Headers**: 1.5rem, font-weight: 600, letter-spacing: -0.01em
- **Metric Values**: 2rem, font-weight: 700, color: var(--text-accent)
- **Body Text**: 1rem, font-weight: 400, line-height: 1.6
- **Small Text**: 0.875rem, font-weight: 500, opacity: 0.8

## Glass Card Components

### Primary Glass Cards (Metrics)
```css
.glass-metric-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    background: rgba(255, 255, 255, 0.2);
}
```

### Secondary Glass Cards (Charts)
```css
.glass-chart-container {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(15px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 20px;
    margin-bottom: 20px;
}
```

## Neumorphic Elements

### Sidebar Filters (Neumorphic Style)
```css
.neuro-sidebar {
    background: #f0f0f3;
    border-radius: 20px;
    padding: 24px;
    box-shadow: inset 8px 8px 16px #d1d1d4, inset -8px -8px 16px #ffffff;
}

.neuro-filter-item {
    background: #f0f0f3;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 4px 4px 8px #d1d1d4, -4px -4px 8px #ffffff;
    transition: all 0.2s ease;
}

.neuro-filter-item:active {
    box-shadow: inset 2px 2px 4px #d1d1d4, inset -2px -2px 4px #ffffff;
}
```

### Interactive Elements
```css
.neuro-button {
    background: #f0f0f3;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    box-shadow: 6px 6px 12px #d1d1d4, -6px -6px 12px #ffffff;
    transition: all 0.2s ease;
}

.neuro-button:hover {
    box-shadow: 8px 8px 16px #d1d1d4, -8px -8px 16px #ffffff;
}

.neuro-button:active {
    box-shadow: inset 3px 3px 6px #d1d1d4, inset -3px -3px 6px #ffffff;
}
```

## Streamlit Custom CSS Implementation

### Main Dashboard Styling
```python
st.markdown("""
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global styles */
.main .block-container {
    padding: 2rem 3rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

/* Header styling */
.main h1 {
    font-family: 'Inter', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* Metric cards glassmorphism */
[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(20px);
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    background: rgba(255, 255, 255, 0.2) !important;
}

/* Chart containers */
.element-container {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(15px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 20px;
    margin-bottom: 20px;
}

/* Sidebar neumorphic styling */
.css-1d391kg {
    background: #f0f0f3 !important;
    border-radius: 20px;
    padding: 24px;
    box-shadow: inset 8px 8px 16px #d1d1d4, inset -8px -8px 16px #ffffff;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 8px;
    backdrop-filter: blur(10px);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 10px;
    color: white;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(255, 255, 255, 0.1);
}

.stTabs [aria-selected="true"] {
    background: rgba(255, 255, 255, 0.2) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)
```

## Chart Styling Guidelines

### Plotly Chart Configurations
```python
# Glass-themed chart template
glass_template = {
    'layout': {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {
            'family': 'Inter, sans-serif',
            'color': 'white'
        },
        'colorway': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'],
        'margin': {'l': 20, 'r': 20, 't': 40, 'b': 20},
        'xaxis': {
            'gridcolor': 'rgba(255,255,255,0.1)',
            'zerolinecolor': 'rgba(255,255,255,0.2)'
        },
        'yaxis': {
            'gridcolor': 'rgba(255,255,255,0.1)',
            'zerolinecolor': 'rgba(255,255,255,0.2)'
        }
    }
}

# Apply to charts
fig.update_layout(glass_template['layout'])
```

## Interactive Elements

### Hover Effects
- **Cards**: Subtle lift (4px translate) with enhanced shadow
- **Buttons**: Soft glow effect with color transition
- **Charts**: Highlight data points with glass overlay

### Loading States
```css
.loading-glass {
    background: linear-gradient(45deg, 
        rgba(255,255,255,0.1) 25%, 
        rgba(255,255,255,0.2) 50%, 
        rgba(255,255,255,0.1) 75%);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
```

## Responsive Design

### Mobile Adaptations
- **Glass cards**: Reduced blur (5px) for performance
- **Neumorphic elements**: Smaller shadows for touch interfaces
- **Typography**: Increased contrast for readability

### Tablet Optimizations
- **Sidebar**: Collapsible with glass overlay
- **Charts**: Adaptive sizing with maintained proportions
- **Touch targets**: Minimum 44px for accessibility

## Accessibility Considerations

### Contrast Ratios
- **Primary text on glass**: Minimum 4.5:1 contrast
- **Interactive elements**: Clear focus indicators
- **Color coding**: Additional shape/pattern indicators

### Motion Preferences
```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

## Performance Optimizations

### CSS Optimizations
- **backdrop-filter**: Progressive enhancement
- **Animations**: Hardware acceleration with `will-change`
- **Glass effects**: Reduced on mobile for better performance

### Loading Strategy
1. **Critical CSS**: Inline essential styles
2. **Progressive enhancement**: Layer advanced effects
3. **Fallbacks**: Solid backgrounds for unsupported browsers

## Implementation Checklist

- [ ] Set up custom CSS with glassmorphism variables
- [ ] Implement neumorphic sidebar components
- [ ] Configure Plotly charts with glass theme
- [ ] Add hover and transition effects
- [ ] Test responsive breakpoints
- [ ] Validate accessibility standards
- [ ] Performance audit on mobile devices
- [ ] Cross-browser compatibility testing

This design guide ensures a cohesive, modern aesthetic that enhances the user experience while maintaining excellent performance and accessibility standards.