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
                "description": "Box plots and radar bar charts showing data spread, outliers, and categorical distributions"
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
    "title": "Map Analysis - Geographic Visualization",
    "overview": "Animated choropleth maps showing spatial patterns of inequality across South Asia. Watch how indicators evolve over time with powerful animation controls and detailed country insights.",
    "features": [
        {
            "name": "Animated Choropleth",
            "description": "Color-coded maps that play through years."
        },
        {
            "name": "Interactive Country Spotlight",
            "description": "Select any country to see detailed performance analysis, historical trends, and regional comparisons"
        }, 
        {
            "name": "Dynamic Storytelling",
            "description": "Year-specific narratives highlighting champions, challengers, and biggest changes"
        },
        {
            "name": "Achievement Badges",
            "description": "Visual indicators for best performers, most improved, and countries needing attention"
        },
        {
            "name": "Historical Trend Charts",
            "description": "Sparkline visualizations comparing country performance against regional averages"
        },
        {
            "name": "Heat Intensity Indicators",
            "description": "Color-coded severity levels (Low, Moderate, High, Critical) for quick assessment"
        },
        {
            "name": "Multi-Format Export",
            "description": "Download maps as images (PNG, JPEG, SVG, PDF), data (CSV, Excel, JSON), or interactive HTML"
        },
        {
            "name": "Year-Over-Year Rankings",
            "description": "Tabular view with multiple years side-by-side showing ranks, trends, and status"
        }            
    ],
    "how_to_use": [
        "The map loads automatically with animation starting from the latest year",
        "Use the Play/Pause button below the map to control animation",
        "Drag the year slider to jump to specific years instantly",
        "Hover over any country to see detailed metrics including value, rank, change, population, and GDP",
        "Use the year slider above the storytelling section for detailed insights",
        "Select a country from the Country Spotlight dropdown for in-depth analysis",
        "View achievement badges to quickly identify top performers and areas of concern",
        "Check the 'Biggest Changes' section to see most improved and most declined countries",
        "Scroll to Rankings table to compare countries across multiple recent years",
        "Select your preferred export format from the dropdown to download visualizations or data"
    ],
    "tips": [
        "Darker colors on the map indicate higher values - what this means depends on your selected indicator",
        "The animation automatically starts at the latest year, not the earliest",
        "Country Spotlight shows a sparkline chart comparing the country against regional average over time",
        "Heat intensity is context-aware: Green (Low 0-25%), Yellow (Moderate 25-50%), Orange (High 50-75%), Red (Critical 75-100%)",
        "Achievement badges update dynamically for each year - check who's leading and who needs attention",
        "Export as HTML to preserve full interactivity including animation and hover details",
        "Use PNG/PDF for reports, SVG for scalable graphics, and CSV/Excel for data analysis",
        "The storytelling section uses flags and visual cards to make data more engaging",
        "Rankings table shows 'Status' (Above avg, Near avg, Below avg) for quick scanning",
    ],
    "common_issues": [
        {
            "problem": "Countries appear in gray",
            "solution": "Gray indicates no data available for that country in your selected indicator and year range. Check Data Quality page for coverage details."
        },
        {
            "problem": "Country Spotlight shows 'No data available'",
            "solution": "The selected country doesn't have data for the chosen year. Try a different year using the slider above the spotlight section."
        },
        {
            "problem": "Rankings table is empty",
            "solution": "No data exists for recent years. This happens with indicators that aren't frequently updated. Try expanding your year range."
        },
        {
            "problem": "What does 'change from previous year' mean?",
            "solution": "It's the absolute difference from the prior year. Positive = increased, Negative = decreased. Arrows show: ⬆️ increase, ⬇️ decrease, ➡️ stable."
        },
        {
            "problem": "Regional average seems wrong",
            "solution": "Regional average is calculated only from countries with data in that specific year. It excludes missing countries, which may affect the value."
        },
    ]
},
    
    "correlations": {
        "title": "Correlations - Inequality Drivers",
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
    
    "Indicator Insights": {
    "title": "Indicator Insights Explorer",
    "overview": (
        "A dominance-based visual explorer showing which indicators stand out within each country "
        "for a selected year. Values are normalized per indicator (0–100) to enable fair comparison, "
        "with a simple descriptive inequality signal derived from inequality-related indicators."
    ),
    "features": [
        {
            "name": "Sunburst Dominance View",
            "description": (
                "Hierarchical view (Region → Country → Indicator) where slice size reflects normalized dominance, "
                "not raw indicator values."
            )
        },
        {
            "name": "Data Availability Context",
            "description": (
                "Highlights visible data coverage per country-year to avoid confusing missing data with low inequality."
            )
        },
        {
            "name": "Country Story (Inequality Signal)",
            "description": (
                "Relative inequality signal based on Gini, income shares, poverty, and unemployment. Descriptive, not causal."
            )
        },
        {
            "name": "Country Spotlight (Bubble View)",
            "description": (
                "Focused bubble chart for a single country where bubble size represents normalized dominance."
            )
        },
        {
            "name": "Top Dominant Indicators",
            "description": (
                "Displays indicators with the highest overall dominance across selected countries."
            )
        }
    ],
    "how_to_use": [
        "Select a year (and color scheme) from the sidebar.",
        "Refer to the chart guide below the sunburst to understand size and color meanings.",
        "Hover over segments to view actual values and normalized dominance.",
        "Compare countries using the country-wise inequality signal.",
        "Use Country Spotlight to examine dominant indicators for a single country."
    ],
    "tips": [
        "Country circle size represents data availability, not inequality.",
        "Slice size reflects indicator dominance after normalization (0–100).",
        "Color intensity shows relative dominance, not good or bad performance.",
        "Inequality signals are relative to the selected countries and year.",
        "Missing segments usually indicate missing data for that year."
    ],
    "common_issues": [
        {
            "problem": "One country appears larger than others",
            "solution": (
                "Circle size reflects data coverage, not inequality. Compare indicator composition and inequality signals instead."
            )
        },
        {
            "problem": "Colors appear to indicate good or bad performance",
            "solution": (
                "Colors represent normalized dominance intensity only. Use tooltips for actual values."
            )
        },
        {
            "problem": "Some indicators or countries are missing",
            "solution": (
                "This usually indicates missing data for the selected year. Try another year or consult the Data Quality page."
            )
        }
    ]
},

    
    "simulator": {
        "title": " Income Simulator - What-If Analysis",
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
    "title": "Temporal Comparison - Then vs Now",
    "overview": "Compare inequality patterns across different time periods with side-by-side visualizations. Analyze how countries have progressed or regressed over time using statistical comparisons and multiple visualization types.",
    "features": [
        {
            "name": "Dual Time Period Selection",
            "description": "Compare two specific years or averaged time ranges for robust analysis"
        },
        {
            "name": "Multiple Visualization Types",
            "description": "Choose from choropleth maps, bar charts, scatter plots, Ranking Shift, Distribution Comparison, Delta Map (Change Visualization), Sankey Diagram (Rank Flow), Heatmap Matrix."
        },
        {
            "name": "Statistical Significance Testing",
            "description": "Paired t-test analysis to determine if observed changes are statistically meaningful"
        },
        {
            "name": "Side-by-Side Maps",
            "description": "Visual comparison of geographic patterns between THEN and NOW periods"
        },
        {
            "name": "Change Metrics Dashboard",
            "description": "Summary statistics including mean change, improvement count, and regional trends"
        },
        {
            "name": "Country-Specific Analysis",
            "description": "Detailed breakdown showing absolute change, percentage change, and direction for each country"
        },
        {
            "name": "Ranking Evolution",
            "description": "Track how countries moved up or down in regional rankings over time"
        },
        {
            "name": "Export Capabilities",
            "description": "Download comparison data in CSV format for external analysis"
        }
    ],
    "how_to_use": [
        "Select your indicator from the dropdown (e.g., GINI index, Income share, Poverty rate)",
        "Choose a color scheme that makes differences easily visible",
        "In the sidebar, select THEN year (earlier period) and NOW year (later period)",
        "Pick your preferred visualization type from the dropdown",
        "Review the Summary Statistics section for overall trends and statistical significance",
        "Examine the main visualization to see spatial or comparative patterns",
        "Scroll to the Detailed Country Analysis table for specific country changes",
        "Use the export button to download the comparison data as CSV"
    ],
    "tips": [
        "For volatile indicators, use averaged ranges rather than single years to reduce noise",
        "A p-value < 0.05 in the statistical test means changes are likely real, not random fluctuations",
        "Scatter plots with the diagonal line clearly show improvers (above line) vs. decliners (below line)",
        "Use Map view for geographic patterns, Bar chart for magnitude comparisons, Scatter for correlation",
        "Ranking Shift view is best for understanding relative position changes, not absolute values",
        "Color schemes matter: diverging scales (RdYlGn) work well for showing positive/negative changes",
        "Check sample size (n) in statistics - comparisons with fewer countries are less reliable",
        "Green cells in the table indicate improvement (lower inequality), red indicates worsening",
        "Export the data table to Excel for creating custom charts or deeper analysis"
    ],
    "common_issues": [
        {
            "problem": "No overlapping countries between periods",
            "solution": "Some countries lack data for one or both periods. Try different years or add more countries in Home configuration."
        },
        {
            "problem": "Statistical test shows 'Not significant' but I see changes",
            "solution": "The changes exist but could be due to random variation. With small samples or high variance, real changes might not reach statistical significance."
        },
        {
            "problem": "Maps look identical even though data changed",
            "solution": "Visual differences can be subtle if changes are small. Check the data table for exact values or try Bar/Scatter visualizations for clearer comparisons."
        },
        {
            "problem": "Percentage change shows as inf or very large numbers",
            "solution": "This happens when the THEN value is zero or very close to zero. Focus on absolute change instead for these cases."
        },
        {
            "problem": "Why do averaged ranges give different results than single years?",
            "solution": "Averaging smooths out year-to-year fluctuations and provides more stable comparisons, especially for indicators with irregular data collection."
        },
        {
            "problem": "Ranking shifted but value barely changed",
            "solution": "Rankings are relative. A country can move in rankings if other countries changed more, even with minimal absolute change."
        },
        {
            "problem": "Can't select the exact years I want",
            "solution": "Year availability depends on data coverage. Check the Data Quality page to see which years have data for your selected countries."
        },
        {
            "problem": "What does 'Mean Absolute Change' mean?",
            "solution": "It's the average of all absolute differences (ignoring direction). Shows typical magnitude of change across all countries."
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