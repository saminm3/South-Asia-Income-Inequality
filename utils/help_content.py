"""
Help Content Database
Contains page-specific help content for the contextual help system
"""

HELP_CONTENT = {
    "home": {
        "title": "Home - Getting Started",
        "overview": "The Home page is your starting point for analyzing inequality data. Configure your analysis parameters here, and they'll apply across all dashboard pages.",
        "features": [
            {
                "name": "Quick Stats",
                "description": "Overview of available countries, indicators, years, and data points"
            },
            {
                "name": "Navigation Cards",
                "description": "Quick access buttons to jump to any analysis page"
            },
            {
                "name": "Auto-Save Configuration",
                "description": "Your settings update automatically - no 'Save' button needed"
            },
            {
                "name": "Visual Preview",
                "description": "See your current configuration at a glance"
            }
        ],
        "how_to_use": [
            "Review the platform statistics at the top",
            "Click navigation cards to explore different analysis pages",
            "Scroll down to customize your analysis settings",
            "Select countries, year range, indicator, and color scheme",
            "Settings apply automatically across all pages"
        ],
        "tips": [
            "Start with a few countries to keep visualizations clear",
            "Use recent years (last 10-15 years) for better data quality",
            "GINI index is the most common inequality measure",
            "Color schemes affect how data is displayed on maps and charts"
        ],
        "common_issues": [
            {
                "problem": "Configuration not applying to pages",
                "solution": "Make sure you've selected at least one country. Settings update automatically when changed."
            },
            {
                "problem": "Don't see my country",
                "solution": "Check if the country has data by visiting the Data Quality page. Some countries have limited coverage."
            }
        ]
    },
    
    "dashboard": {
        "title": "Dashboard - Multi-Dimensional Overview",
        "overview": "Comprehensive statistical overview with temporal trends, country comparisons, and distribution analysis. Perfect for getting a complete picture of inequality patterns.",
        "features": [
            {
                "name": "Temporal Trends",
                "description": "Line charts showing how indicators change over time"
            },
            {
                "name": "Country Comparison",
                "description": "Side-by-side bar charts comparing selected countries"
            },
            {
                "name": "Distribution Analysis",
                "description": "Box plots showing data spread, outliers, and quartiles"
            },
            {
                "name": "Summary Statistics",
                "description": "Mean, maximum, minimum values with country identifications"
            },
            {
                "name": "Rankings Table",
                "description": "Sortable table ranking countries by indicators"
            }
        ],
        "how_to_use": [
            "View automatic visualizations based on your Home configuration",
            "Use sidebar filters to adjust countries or years on the fly",
            "Switch between line charts, bar charts, and box plots",
            "Hover over charts to see exact values",
            "Click download buttons to export charts or data"
        ],
        "tips": [
            "Box plots are great for seeing inequality spread and outliers",
            "Hover over any chart for detailed tooltips",
            "Use the rankings table to quickly identify top/bottom performers",
            "Export both the visualizations AND underlying data for reports"
        ],
        "common_issues": [
            {
                "problem": "Chart looks empty or sparse",
                "solution": "Try expanding your year range or selecting more countries. Some indicators have limited data."
            },
            {
                "problem": "Can't see all countries in legend",
                "solution": "Too many countries selected. Try selecting 3-5 for clearer visualization."
            }
        ]
    },
    
    "map": {
        "title": " Map Analysis - Geographic Visualization",
        "overview": "Animated choropleth maps showing spatial patterns of inequality across South Asia. Watch how regions evolve over time with powerful animation controls.",
        "features": [
            {
                "name": "Animated Choropleth",
                "description": "Color-coded maps that play through years automatically"
            },
            {
                "name": "Multiple Projections",
                "description": "View maps in different geographical projections"
            },
            {
                "name": "Country Highlighting",
                "description": "Add red borders to focus on specific countries"
            },
            {
                "name": "Color Schemes",
                "description": "Choose from 7+ color palettes for optimal visualization"
            },
            {
                "name": "Dynamic Insights",
                "description": "Year-specific statistics: highest, lowest, most improved"
            },
            {
                "name": "Rankings Table",
                "description": "Tabular view with multiple years side-by-side"
            }
        ],
        "how_to_use": [
            "Enable animation to see changes over time",
            "Adjust animation speed with the slider (lower = faster)",
            "Select countries to highlight with red borders",
            "Choose different map projections for better viewing angles",
            "Use the year slider below the map for detailed insights",
            "Check the rankings table for precise comparisons"
        ],
        "tips": [
            "Animation speed 500-800ms works best for presentations",
            "Hover over countries to see detailed statistics + metadata",
            "Use 'Natural Earth' projection for familiar map view",
            "Country highlighting helps when focusing on specific regions",
            "Download map as PNG for high-quality report images"
        ],
        "common_issues": [
            {
                "problem": "Map animation too fast/slow",
                "solution": "Adjust the 'Animation Speed' slider in the sidebar. Lower values = faster animation."
            },
            {
                "problem": "Countries appear gray",
                "solution": "Gray means no data available for that country/year. Check Data Quality page."
            },
            {
                "problem": "Can't see highlighted countries",
                "solution": "Make sure countries are selected in the 'Highlight Countries' dropdown in sidebar."
            }
        ]
    },
    
    "correlations": {
        "title": " Correlations - Inequality Drivers",
        "overview": "Discover relationships between inequality indicators and potential drivers like GDP, education, and technology. Uses statistical analysis to identify patterns.",
        "features": [
            {
                "name": "Scatter Plots",
                "description": "Visualize relationships between two indicators"
            },
            {
                "name": "Trend Lines",
                "description": "See correlation direction with best-fit lines"
            },
            {
                "name": "Statistical Analysis",
                "description": "Pearson correlation coefficient and p-value"
            },
            {
                "name": "Strength Assessment",
                "description": "Automatic classification: Strong, Moderate, Weak"
            },
            {
                "name": "Country Rankings",
                "description": "Inequality level snapshot based on selected indicator"
            }
        ],
        "how_to_use": [
            "Select an inequality indicator for the Y-axis (e.g., GINI)",
            "Choose a potential driver for the X-axis (e.g., GDP, Education)",
            "Adjust year range if needed to see more/fewer data points",
            "Toggle trend line to see correlation direction",
            "Read the 'Scatter View Story' for interpretation",
            "Check country rankings to see relative inequality levels"
        ],
        "tips": [
            "Try different pairs: GDP vs GINI, Education vs Inequality",
            "r > 0.7 means strong correlation (positive or negative)",
            "p < 0.05 means the pattern is statistically reliable",
            "Expand 'Why some countries missing' to understand data coverage",
            "Correlation doesn't prove causation - it shows patterns only"
        ],
        "common_issues": [
            {
                "problem": "Not enough data points",
                "solution": "Expand the year range. Correlations need overlapping data for both X and Y indicators."
            },
            {
                "problem": "Why are some countries missing?",
                "solution": "Countries only appear if they have BOTH selected indicators available in the chosen years."
            },
            {
                "problem": "What does negative correlation mean?",
                "solution": "Negative (r < 0) means as one increases, the other decreases. Example: More education → Less inequality."
            }
        ]
    },
    
    "sunburst": {
        "title": "Sunburst - Hierarchical Explorer",
        "overview": "Radial visualization showing indicator dominance across countries. Click segments to drill down and explore the hierarchy interactively.",
        "features": [
            {
                "name": "Interactive Zoom",
                "description": "Click any segment to zoom in for detailed view"
            },
            {
                "name": "Normalized Scale",
                "description": "All indicators scaled 0-100 for fair comparison"
            },
            {
                "name": "Color Coding",
                "description": "Darker colors indicate higher dominance"
            },
            {
                "name": "Country Spotlight",
                "description": "Navigate through countries one-by-one with bubble charts"
            },
            {
                "name": "Inequality Signals",
                "description": "Automatic classification: High, Moderate, Lower"
            }
        ],
        "how_to_use": [
            "Select a year to analyze from the sidebar",
            "Choose your preferred color scheme",
            "Click on any segment to zoom in",
            "Read the 'Visualization Story' for country-wise insights",
            "Use Previous/Next buttons in Country Spotlight",
            "Expand individual country sections for detailed explanations"
        ],
        "tips": [
            "Click the center to zoom back out",
            "Bigger slices = more dominant indicators (after normalization)",
            "Inequality signal uses GINI, income-share, poverty, unemployment",
            "Country Spotlight bubble chart shows all indicators for one country",
            "This shows patterns, not absolute inequality levels"
        ],
        "common_issues": [
            {
                "problem": "Sunburst looks confusing",
                "solution": "Start with Country Spotlight mode instead. It's easier to understand one country at a time."
            },
            {
                "problem": "Why 'dominance' not 'inequality'?",
                "solution": "Dominance shows what stands out after normalization. We use inequality indicators to build a simple signal."
            },
            {
                "problem": "Can't find my country",
                "solution": "Use the expandable sections in 'Visualization Story' or click Previous/Next in Country Spotlight."
            }
        ]
    },
    
    "simulator": {
        "title": "Income Simulator - Scenario Modeling",
        "overview": "Interactive tool to understand how different factors affect income distribution. Adjust education, gender, location, and digital access to see estimated percentile rankings.",
        "features": [
            {
                "name": "Education Slider",
                "description": "Adjust years of schooling (0-20 years)"
            },
            {
                "name": "Digital Access",
                "description": "Internet connectivity percentage (0-100%)"
            },
            {
                "name": "Gender Selection",
                "description": "See the impact of gender wage gaps"
            },
            {
                "name": "Location Toggle",
                "description": "Compare urban vs rural income differences"
            },
            {
                "name": "Real-time Calculation",
                "description": "Instant percentile updates as you adjust sliders"
            },
            {
                "name": "Country Comparison",
                "description": "Same profile = different results across countries"
            }
        ],
        "how_to_use": [
            "Select a country from the dropdown",
            "Adjust the education years slider",
            "Set digital access percentage",
            "Choose gender (Male/Female)",
            "Select location (Urban/Rural)",
            "View estimated income percentile in the gauge chart",
            "Try different combinations to explore patterns",
            "Compare the same profile across different countries"
        ],
        "tips": [
            "Education usually has the strongest impact on income",
            "Gender gap varies significantly by country",
            "Urban areas typically show 10-20 percentile advantage",
            "Digital access is increasingly important in modern economies",
            "Try extreme scenarios to understand range of possibilities"
        ],
        "common_issues": [
            {
                "problem": "Results seem unrealistic",
                "solution": "This is a simplified educational model. Real income depends on many more complex factors."
            },
            {
                "problem": "Same inputs, different countries = different results",
                "solution": "That's correct! Each country has different economic structures and opportunity distributions."
            },
            {
                "problem": "What does percentile mean?",
                "solution": "50th percentile = middle (half earn more, half earn less). 90th = top 10%. 10th = bottom 10%."
            }
        ]
    },
    
    "temporal": {
        "title": "Temporal Comparison - Then vs Now",
        "overview": "Compare inequality patterns across different time periods using statistical tests. See which countries improved, which declined, and by how much.",
        "features": [
            {
                "name": "Point-to-Point Mode",
                "description": "Compare two specific years (e.g., 2000 vs 2020)"
            },
            {
                "name": "Range-to-Range Mode",
                "description": "Compare averaged periods (e.g., 2000-2005 vs 2015-2020)"
            },
            {
                "name": "Multiple Visualizations",
                "description": "Choropleth maps, bar charts, scatter plots, ranking shifts"
            },
            {
                "name": "Statistical Testing",
                "description": "Paired t-test to determine if changes are significant"
            },
            {
                "name": "Change Metrics",
                "description": "Absolute change, percentage change, rank change"
            }
        ],
        "how_to_use": [
            "Select your indicator from the dropdown",
            "Choose color scheme and comparison mode",
            "For Point-to-Point: Select THEN and NOW years",
            "For Range-to-Range: Select early and late periods",
            "Pick visualization type (Map, Bar, Scatter, Ranking, Table)",
            "Read the Summary section for statistical interpretation",
            "Download results as CSV for further analysis"
        ],
        "tips": [
            "Point-to-Point is good for specific events (e.g., policy changes)",
            "Range-to-Range smooths out yearly fluctuations",
            "Scatter plot with diagonal line shows who improved (above line)",
            "Check p-value: p < 0.05 means change is statistically significant",
            "Ranking Shift shows countries moving up/down in relative terms"
        ],
        "common_issues": [
            {
                "problem": "No overlapping countries",
                "solution": "Some countries don't have data for both time periods. Try different years or use more countries."
            },
            {
                "problem": "What does 'statistically significant' mean?",
                "solution": "It means the change is unlikely due to random chance (p < 0.05 is the standard threshold)."
            },
            {
                "problem": "Maps look similar but stats show change",
                "solution": "Small visual differences can be statistically significant. Check the percentage changes in the table."
            }
        ]
    },
    
    "search": {
        "title": " Smart Search - Quick Navigation",
        "overview": "Keyboard-friendly search system for finding data, countries, indicators, and commands.",
        "features" : [
            {
                "name": "Multi-Category Search",
                "description": "Search countries, indicators, years, commands, filters, and data"
            },
            {
                "name": "Quick Actions",
                "description": "One-click shortcuts to common pages"
            },
            {
                "name": "Bookmarked Views",
                "description": "Pre-configured queries for common analysis needs"
            },
            {
                "name": "Search History",
                "description": "Re-run your last 10 searches with one click"
            },
            {
                "name": "Natural Language",
                "description": "Type like you speak (e.g., 'high inequality countries')"
            }
        ],
        "how_to_use": [
            "Type in the search box (or press Ctrl+K to focus)",
            "Results appear automatically in categorized tabs",
            "Click on results to see more details or take action",
            "Use Quick Actions for instant page navigation",
            "Select bookmarked views for common analysis scenarios",
            "Click recent searches to repeat previous queries"
        ],
        "tips": [
            "Search 'Bangladesh 2020' for specific country-year data",
            "Type 'GINI' to find all GINI-related indicators",
            "Use commands like 'export', 'map', 'correlation' for navigation",
            "Natural language works: 'high inequality' suggests filters",
            "Check Search History to quickly repeat previous queries"
        ],
        "common_issues": [
            {
                "problem": "No results found",
                "solution": "Try shorter keywords or synonyms. Search is case-insensitive and matches partial words."
            },
            {
                "problem": "Too many results",
                "solution": "Be more specific. Add year, country, or indicator name to narrow results."
            },
            {
                "problem": "Bookmark doesn't work",
                "solution": "Bookmarks show recommendations. You still need to navigate to the suggested page manually."
            }
        ]
    },
    
    "quality": {
        "title": " Data Quality - Transparency Report",
        "overview": "Comprehensive data completeness monitoring and source reliability tracking. Understand data limitations before drawing conclusions.",
        "features": [
            {
                "name": "Completeness Dashboard",
                "description": "Visual heatmap showing data availability by country/indicator"
            },
            {
                "name": "Quality Badges",
                "description": "Color-coded indicators: Green (High), Yellow (Moderate), Red (Low)"
            },
            {
                "name": "Source Tracking",
                "description": "Shows data origin (World Bank, UNDP, National sources)"
            },
            {
                "name": "Gap Identification",
                "description": "Highlights missing years and incomplete coverage"
            },
            {
                "name": "Last Updated Timestamps",
                "description": "Know when data was most recently refreshed"
            }
        ],
        "how_to_use": [
            "View the completeness heatmap for overall coverage",
            "Check quality badges for specific country-indicator pairs",
            "Expand 'Quality Details' table for precise percentages",
            "Use this page BEFORE major analysis to understand limitations",
            "Reference gaps when interpreting results"
        ],
        "tips": [
            "Green badges (80%+) = reliable for analysis",
            "Yellow badges (60-79%) = use with caution",
            "Red badges (<60%) = insufficient for strong conclusions",
            "GINI data tends to have more gaps (expensive surveys)",
            "Economic indicators (GDP, Labor) usually have better coverage"
        ],
        "common_issues": [
            {
                "problem": "Why so many gaps?",
                "solution": "Inequality data requires expensive household surveys. Many countries only collect every 3-5 years."
            },
            {
                "problem": "Is missing data filled/estimated?",
                "solution": "No. We never fill gaps with estimates to preserve data integrity. Missing = truly missing."
            }
        ]
    },
    
    "help": {
        "title": "❓ Help & Documentation - Full Guide",
        "overview": "Comprehensive user manual covering all platform features, common tasks, keyboard shortcuts, and troubleshooting.",
        "features": [
            {
                "name": "Quick Start Guide",
                "description": "Get started in 3 simple steps"
            },
            {
                "name": "Page-by-Page Tutorials",
                "description": "Detailed guide for every analysis page"
            },
            {
                "name": "Common Tasks",
                "description": "How-to guides for frequent operations"
            },
            {
                "name": "Keyboard Shortcuts",
                "description": "Speed up your workflow with hotkeys"
            },
            {
                "name": "Troubleshooting",
                "description": "Solutions to common issues and errors"
            },
            {
                "name": "Data Methodology",
                "description": "Sources, processing, and indicator definitions"
            }
        ],
        "how_to_use": [
            "Use the tabs to navigate between sections",
            "Start with 'Quick Start' if you're new",
            "Search within help (Ctrl+F) to find specific topics",
            "Expand collapsible sections for detailed information",
            "Bookmark this page for quick reference"
        ],
        "tips": [
            "The Help page is searchable - use Ctrl+F in your browser",
            "Floating help buttons on each page show quick tips",
            "Check 'Common Tasks' for step-by-step guides",
            "Data Methodology section explains indicator calculations",
            "Contact information is at the bottom for further assistance"
        ],
        "common_issues": []
    }
}