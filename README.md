# 🤖 AnalytixPro - Your Data Analyst Assistant

AnalytixPro is a comprehensive Streamlit-based web application that transforms CSV data analysis with guided insights. Combining automated exploratory data analysis, interactive visualizations, natural language querying, and smart recommendations, AnalytixPro makes advanced data analysis accessible to everyone without relying on external AI services.

![AnalytixPro](https://img.shields.io/badge/Data-Assistant-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)

## ✨ Key Features

### 📊 Comprehensive Data Analysis
- **Drag & Drop CSV Upload**: Simple file upload with automatic validation and error handling
- **Demo Dataset**: Built-in sample employee dataset for immediate testing
- **Automated EDA**: Complete exploratory data analysis with statistical summaries, distribution plots, and correlation analysis
- **Data Quality Assessment**: Missing value detection, duplicate analysis, outlier identification, and data type profiling
- **Interactive Data Tables**: Sortable, filterable tables with real-time metrics

### 🔍 Guided Intelligence (No Cloud AI)
- **Natural Language Queries**: Ask questions about your data in plain English ("Show me null values", "Find outliers")
- **Automated Insights**: On-device heuristics for patterns, trends, and data quality
- **Smart Data Cleaning**: Built-in recommendations for data preprocessing and quality improvement
- **Predictive Hints**: Lightweight suggestions for modeling approaches

### 📈 Advanced Visualizations
- **Intelligent Chart Selection**: Auto-recommended visualizations based on data characteristics
- **Multiple Chart Types**: Histograms, scatter plots, line charts, bar charts, box plots, correlation heatmaps
- **Publication-Ready Quality**: matplotlib and seaborn integration with professional styling
- **Interactive Features**: Hover tooltips, zoom capabilities, and customizable chart options

### 💬 Interactive Experience
- **Guided Dialogue**: Natural language queries with contextual memory inside the app
- **Voice Command Support**: Text-to-speech and speech recognition for hands-free analysis
- **Quick Action Buttons**: One-click access to common analysis tasks
- **Context-Aware Responses**: Uses your dataset context for relevant suggestions without external models

### 📤 Professional Export & Reporting
- **Multi-Format Export**: CSV, Excel (multi-sheet), and PDF report generation
- **Comprehensive PDF Reports**: Professional reports with charts, statistics, and AI insights
- **Excel Workbooks**: Separate sheets for data, statistics, data info, and missing value analysis
- **Custom Formatting**: Well-structured reports suitable for stakeholders

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**: Required for all dependencies

### 🔧 Installation & Setup

1. **Navigate to the Project**
```bash
cd AnalytixPro
```

2. **Install Dependencies**
```bash
# One-line installation (recommended)
pip install streamlit pandas numpy matplotlib seaborn scipy speechrecognition pyttsx3 reportlab weasyprint openpyxl

# Or using uv (faster)
uv add streamlit pandas numpy matplotlib seaborn scipy speechrecognition pyttsx3 reportlab weasyprint openpyxl

# See dependencies.txt for troubleshooting and alternatives
```
3. **Run the Application**
```bash
streamlit run app.py --server.port 5000
```

4. **Access the Application**
Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
analytixpro/
├── app.py                      # Main Streamlit application
├── demo_data.csv              # Sample dataset for testing
├── dependencies.txt           # Python dependencies list
├── README.md                  # This file
├── replit.md                  # Project documentation
├── pyproject.toml             # Project configuration
├── uv.lock                    # Dependency lock file
├── assets/
│   └── dark_mode.css         # Custom CSS styling
└── modules/
    ├── __init__.py           # Module initialization
    ├── eda.py                # Exploratory Data Analysis
    ├── chart_gen.py          # Chart generation and visualization
    ├── query_parser.py       # Natural language query processing
    ├── voice_handler.py      # Voice command processing
    └── export.py             # Data export and report generation
```

## 🎯 How to Use

### 1. Upload Your Data
- Drag and drop a CSV file or click to browse
- Use the "Load Demo Dataset" button to try with sample data
- View automatic data overview with key metrics

### 2. Explore Your Data
- **EDA Report**: Click "Generate EDA Report" for comprehensive analysis
- **Query Data**: Ask questions in plain English like "Show me null values"
- **Visualizations**: Generate charts automatically or choose specific types
 - **Data Tips**: Follow inline suggestions for cleaning and exploration

### 3. Get Insights
- Use quick action buttons: "Generate Insights", "Suggest Cleaning", "Predict Trends"
- Ask specific questions about your data in the chat interface
- Get built-in recommendations for data improvement and analysis

### 4. Export Results
- Download cleaned data as CSV or Excel
- Generate professional PDF reports with charts and insights
- Share findings with stakeholders

## 🔍 Example Queries

AnalytixPro understands natural language queries about your data:

**Data Exploration:**
- "Show me null values"
- "What are the data types?"
- "Give me basic statistics"
- "Show correlation between columns"

**Data Quality:**
- "Find outliers"
- "Show duplicate rows"
- "Count missing values"
- "What's the data quality?"

**Analysis:**
- "Show first 10 rows"
- "What are unique values in [column]?"
- "Find patterns in my data"
- "Suggest data cleaning steps"

## 📊 Supported Data Types

- **Numeric**: Integers, floats, percentages
- **Categorical**: Text, categories, labels
- **DateTime**: Dates and timestamps (auto-detected)
- **Boolean**: True/false values
- **Mixed Types**: Automatic detection and handling

## 🛠️ Technical Requirements

### System Requirements
- **Python**: 3.11 or higher
- **Memory**: 4GB+ RAM recommended for large datasets
- **Storage**: 500MB for dependencies and temporary files
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

### Dependencies
- **Core**: `streamlit`, `pandas`, `numpy`
- **Visualization**: `matplotlib`, `seaborn`
- **Voice**: `speechrecognition`, `pyttsx3` (optional)
- **Export**: `reportlab`, `weasyprint`, `openpyxl`
- **Analysis**: `scipy` for statistical functions

## 🔧 Configuration
### Optional Settings
- Voice features work best in local environments
- PDF generation requires system fonts for optimal rendering
- Large datasets (>100MB) may require increased memory

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py --server.port 5000
```

### Replit Deployment
1. Fork this Repl
2. Click "Run" - the app will start automatically

### Streamlit Cloud
1. Connect your GitHub repository
2. Deploy with one click

## 🎨 Customization

### Styling
- Modify `assets/dark_mode.css` for custom themes
- Update color schemes and layouts
- Add custom logos and branding

### Features
- Add new visualization types in `chart_gen.py`
- Create custom query patterns in `query_parser.py`

## 🔍 Troubleshooting

### Common Issues

**Voice Commands Not Working**
- Install audio dependencies: `pip install pyaudio`
- Grant microphone permissions in browser
- Use text-based voice commands in cloud environments

**Large File Upload Issues**
- Check Streamlit's default upload limits
- Consider data sampling for initial analysis
- Use chunked processing for very large datasets

**Chart Generation Errors**
- Ensure sufficient memory for plotting
- Check data types are compatible
- Verify no circular references in data

### Getting Help
- Check the demo dataset to verify functionality
- Review error messages in the Streamlit interface
- Enable debug mode for detailed error logging

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
git clone <repository-url>
cd datasage-ai
pip install -r requirements.txt
streamlit run app.py
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit** for the excellent web framework
- **Pandas & NumPy** for powerful data manipulation
- **Matplotlib & Seaborn** for beautiful visualizations
- **Open Source Community** for the amazing libraries and tools

## 📞 Support

- **Documentation**: Check this README and `replit.md`
- **Issues**: Report bugs via GitHub Issues
- **Questions**: Start a GitHub Discussion
- **Updates**: Follow releases for new features

---

**Made with ❤️ for the data science community**

*AnalytixPro - Making data analysis accessible to everyone*
