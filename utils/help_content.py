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
        "overview": "Comprehensive statistical overview with temporal trends, country comparisons, distribution analysis, and correlation patterns. Perfect for getting a complete picture of inequality dynamics.",
        "features": [
            {
                "name": "Temporal Trends",
                "description": "Line charts showing how indicators change over time"
            },
            {
                "name": "Country Comparison",
                "description": "Side-by-side bar charts comparing selected countries with color-coded inequality levels"
            },
            {
                "name": "Distribution Analysis",
                "description": "Box plots and donut charts showing data spread, outliers, and categorical distributions"
            },
            {
                "name": "Correlation Matrix Heatmap",
                "description": "Interactive heatmap showing pairwise correlations between all countries' inequality patterns. Values displayed in each cell for precise analysis."
            },
            {
                "name": "Summary Statistics",
                "description": "Mean, maximum, minimum values with country identifications and correlation insights"
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
            "Scroll to Correlation Analysis section to see country relationship patterns",
            "Select different color schemes for the correlation heatmap (RdBu_r recommended for academic work)",
            "Hover over heatmap cells to see exact correlation values and country pairs",
            "Click download buttons to export charts, correlation matrix as CSV/SVG, or data",
            "Expand 'Top Correlation Pairs' to see strongest relationships ranked"
        ],
        "tips": [
            "Box plots are great for seeing inequality spread and outliers",
            "Correlation heatmap shows ALL pairwise relationships - perfect for identifying country clusters",
            "Values in heatmap cells are Pearson correlation coefficients (-1 to +1)",
            "RdBu_r color scheme (red-blue) is standard for academic correlation matrices",
            "Strong correlations (r > 0.8) indicate similar inequality trajectories",
            "Negative correlations (r < 0) mean opposite trends - look for these patterns",
            "Use correlation matrix CSV export for further statistical analysis",
            "Statistics cards below heatmap highlight strongest, average, and most divergent pairs",
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
            },
            {
                "problem": "Heatmap values hard to read",
                "solution": "Values are always displayed. Hover over cells for clearer view. White text on light backgrounds can be adjusted in settings."
            },
            {
                "problem": "What does correlation value mean?",
                "solution": "+1 = perfect positive (countries move together), 0 = no relationship, -1 = perfect negative (opposite trends). See interpretation guide below heatmap."
            }
        ]
    },
    
    "map": {
        "title": "🗺️ Map Analysis - Geographic Visualization",
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
        "title": "📊 Correlations - Inequality Drivers",
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
                "name": "Driver Suggestions",
                "description": "Recommends potential factors affecting inequality"
            }
        ],
        "how_to_use": [
            "Select inequality indicator (Y-axis)",
            "Choose potential driver indicator (X-axis)",
            "View scatter plot with trend line",
            "Check correlation strength and statistical significance",
            "Try different indicator combinations",
            "Export charts and statistical results"
        ],
        "tips": [
            "Strong correlation (r > 0.7) suggests meaningful relationship",
            "P-value < 0.05 means relationship is statistically significant",
            "Negative correlation means inverse relationship (one up, other down)",
            "Correlation doesn't mean causation - always consider context",
            "GDP per capita and education often correlate with inequality"
        ],
        "common_issues": [
            {
                "problem": "Low or no correlation",
                "solution": "Not all indicators relate to inequality. Try different combinations or check if data quality is sufficient."
            },
            {
                "problem": "What is p-value?",
                "solution": "P-value measures statistical significance. < 0.05 means the relationship is unlikely due to chance."
            },
            {
                "problem": "Scatter plot looks scattered",
                "solution": "That's normal for weak correlations. Look for trend line direction and r-value to assess strength."
            }
        ]
    },
    
    "sunburst": {
        "title": "☀️ Sunburst - Hierarchical Composition",
        "overview": "Interactive hierarchical visualization showing inequality composition by region, country, and time period. Perfect for understanding nested patterns.",
        "features": [
            {
                "name": "Multi-Level Hierarchy",
                "description": "View data by Region → Country → Year structure"
            },
            {
                "name": "Interactive Drill-Down",
                "description": "Click segments to zoom in, click center to zoom out"
            },
            {
                "name": "Proportional Sizing",
                "description": "Segment size shows relative contribution"
            },
            {
                "name": "Color Gradients",
                "description": "Colors represent inequality levels"
            },
            {
                "name": "Path Tracking",
                "description": "Shows your current location in the hierarchy"
            }
        ],
        "how_to_use": [
            "Start at the outer ring (regions/countries)",
            "Click any segment to zoom in",
            "Click the center circle to zoom back out",
            "Hover over segments for details",
            "Use color to identify high/low inequality areas"
        ],
        "tips": [
            "Larger segments = bigger share of total inequality",
            "Darker colors usually mean higher inequality",
            "Start from center and work outward to understand structure",
            "Compare segment sizes within same ring for relative importance",
            "Export as SVG for high-quality presentations"
        ],
        "common_issues": [
            {
                "problem": "Sunburst looks cluttered",
                "solution": "Too many years/countries. Filter to 2-3 countries or 5-10 years for clearer view."
            },
            {
                "problem": "Can't zoom out",
                "solution": "Click the center circle (innermost circle) to zoom back to root level."
            },
            {
                "problem": "Missing segments",
                "solution": "Countries/years with no data don't appear. Check Data Quality page."
            }
        ]
    },
    
    "simulator": {
        "title": "🎮 Income Simulator - What-If Analysis",
        "overview": "Interactive tool to simulate changes in income inequality under different policy scenarios. Adjust parameters and see real-time impact.",
        "features": [
            {
                "name": "Policy Sliders",
                "description": "Adjust tax rates, transfers, education spending, etc."
            },
            {
                "name": "Real-Time Updates",
                "description": "See GINI coefficient change instantly"
            },
            {
                "name": "Scenario Comparison",
                "description": "Save and compare multiple policy combinations"
            },
            {
                "name": "Lorenz Curve",
                "description": "Visual representation of income distribution"
            },
            {
                "name": "Impact Breakdown",
                "description": "See which policies have biggest effect"
            }
        ],
        "how_to_use": [
            "Start with baseline scenario (no policy changes)",
            "Adjust policy sliders one at a time",
            "Watch GINI coefficient and Lorenz curve update",
            "Save scenarios you want to compare",
            "Export results for reports or presentations"
        ],
        "tips": [
            "Small slider changes can have big impacts - move slowly",
            "Tax changes affect high-income groups most",
            "Transfer programs target low-income groups",
            "Education spending has long-term effects",
            "Save baseline before making changes so you can reset"
        ],
        "common_issues": [
            {
                "problem": "Changes seem unrealistic",
                "solution": "Simulator uses simplified models. Real-world effects are more complex."
            },
            {
                "problem": "GINI doesn't change much",
                "solution": "Some policies have small effects. Try combining multiple policies."
            },
            {
                "problem": "Can't reset to baseline",
                "solution": "Refresh the page or click 'Reset All' button if available."
            }
        ]
    },
    
    "temporal": {
        "title": "📅 Temporal Comparison - Change Over Time",
        "overview": "Compare inequality levels between two time points or periods. Perfect for evaluating policy impacts or long-term trends.",
        "features": [
            {
                "name": "Point-to-Point",
                "description": "Compare two specific years (e.g., 2010 vs 2020)"
            },
            {
                "name": "Range-to-Range",
                "description": "Compare two time periods (e.g., 2005-2010 vs 2015-2020)"
            },
            {
                "name": "Multiple Visualizations",
                "description": "Maps, bar charts, scatter plots, rankings, and tables"
            },
            {
                "name": "Change Metrics",
                "description": "Absolute change, percentage change, and statistical significance"
            },
            {
                "name": "Ranking Shifts",
                "description": "See which countries moved up/down in rankings"
            }
        ],
        "how_to_use": [
            "Select comparison mode (Point-to-Point or Range-to-Range)",
            "For Point-to-Point: Choose two specific years",
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
        "title": "🔍 Smart Search - Quick Navigation",
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
        "title": "✅ Data Quality - Transparency Report",
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