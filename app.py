import streamlit as st
import pandas as pd
import numpy as np
import os
import warnings
from modules import eda, chart_gen, query_parser, export
from modules import data_cleaning

# Suppress warnings for cleaner UI
warnings.filterwarnings('ignore')

def _clean_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataframe to prevent Arrow conversion issues"""
    df_clean = df.copy()
    
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            # Convert to string first to handle all mixed types
            df_clean[col] = df_clean[col].astype(str)
            # Replace 'nan' strings with empty strings
            df_clean[col] = df_clean[col].replace(['nan', 'None', 'NaN'], '')
            # Clean problematic characters that cause Arrow conversion issues
            df_clean[col] = df_clean[col].str.replace('%', '_percent', regex=False)
            df_clean[col] = df_clean[col].str.replace('$', '_dollar', regex=False)
            df_clean[col] = df_clean[col].str.replace(':', '_colon', regex=False)
    
    # Ensure all columns are Arrow-compatible
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            # Replace NaN values with empty strings for object columns
            df_clean[col] = df_clean[col].fillna('')
        # Handle numeric columns
        elif df_clean[col].dtype in ['int64', 'float64']:
            df_clean[col] = df_clean[col].fillna(0)
    
    return df_clean

# Configure page
st.set_page_config(
    page_title="AnalytixPro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
import os
css_path = os.path.dirname(os.path.abspath(__file__))
css_files = [
    os.path.join(css_path, "assets", "dark_mode.css")
]
for css_file in css_files:
    if os.path.exists(css_file):
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Could not load CSS file: {css_file}")

# ===== LANDING PAGE LOGIC =====
# Skip landing page - go directly to main app
if 'show_app' not in st.session_state:
    st.session_state.show_app = True

# ===== MAIN APP STARTS HERE =====
# Header
st.markdown("""
<div class="app-header">
    <h1>🤖 AnalytixPro</h1>
    <p>Your Free Data Analyst Assistant – Upload, Analyze, Export</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("📁 Data Upload")
    uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx", "xls"])
    
    # Demo data buttons (stacked for visibility)
    st.markdown("**Try with sample data:**")
    if st.button("📊 Load Clean Demo", key="btn_demo_clean"):
        try:
            demo_df = pd.read_csv("demo_data.csv")
            st.session_state.demo_data = demo_df
            st.success("Clean CSV dataset loaded!")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading demo data: {str(e)}")
    if st.button("🧹 Load Dirty Demo", key="btn_demo_dirty"):
        try:
            dirty_df = pd.read_csv("demo_dirty_data.csv")
            st.session_state.demo_data = dirty_df
            st.success("Dirty dataset loaded!")
            st.info("Perfect for practicing data cleaning!")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading dirty data: {str(e)}")
    
    # Create demo Excel file if it doesn't exist
    if not os.path.exists("demo_data.xlsx"):
        try:
            demo_df = pd.read_csv("demo_data.csv")
            demo_df.to_excel("demo_data.xlsx", index=False, sheet_name="Employee_Data")
        except:
            pass  # Fail silently if can't create Excel file
    
    st.markdown("**Supported formats:** CSV, Excel (.xlsx, .xls)")
    st.info("💡 For Excel files with multiple sheets, you can select which sheet to analyze")
    
    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        
        # File info
        file_extension = uploaded_file.name.split('.')[-1].upper()
        file_details = {
            "Filename": uploaded_file.name,
            "File type": file_extension,
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.json(file_details)

# Handle demo data or uploaded file
data_source = None
df = None

if uploaded_file is not None:
    try:
        # Determine file type and load accordingly
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            # For Excel files, try to read the first sheet
            try:
                df = pd.read_excel(uploaded_file, sheet_name=0)
                
                # If Excel has multiple sheets, let user choose
                excel_file = pd.ExcelFile(uploaded_file)
                if len(excel_file.sheet_names) > 1:
                    st.info(f"Excel file has {len(excel_file.sheet_names)} sheets. Using first sheet: '{excel_file.sheet_names[0]}'")
                    
                    # Option to select different sheet
                    with st.sidebar:
                        selected_sheet = st.selectbox(
                            "Select Excel sheet:",
                            excel_file.sheet_names,
                            key="sheet_selector"
                        )
                        
                        if selected_sheet != excel_file.sheet_names[0]:
                            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                            st.success(f"Switched to sheet: '{selected_sheet}'")
                            
            except Exception as excel_error:
                st.error(f"Error reading Excel file: {str(excel_error)}")
                st.info("Try saving your Excel file as CSV format")
                df = None
        else:
            st.error("Unsupported file format")
            df = None
        
        if df is not None:
            data_source = "uploaded"
            # Clean data to prevent Arrow conversion issues
            df = _clean_dataframe_for_display(df)
            st.success(f"File loaded successfully! ({len(df)} rows, {len(df.columns)} columns)")
        
    except Exception as e:
        st.error(f"Error loading uploaded file: {str(e)}")
        st.info("Please ensure your file is in CSV or Excel format and properly formatted")

elif 'demo_data' in st.session_state:
    # Use demo data if available
    df = st.session_state.demo_data.copy()
    data_source = "demo"
    
    # Clean data to prevent Arrow conversion issues
    df = _clean_dataframe_for_display(df)
    st.success("Using demo dataset for analysis")

if df is not None:
    try:
        # Use cleaned data if available
        current_df = st.session_state.get('cleaned_data', df)
        is_cleaned = 'cleaned_data' in st.session_state
        
        # Data overview
        st.subheader("📊 Data Overview")
        if is_cleaned:
            st.success("🧹 Using cleaned data")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Rows", len(current_df))
        with col2:
            st.metric("Columns", len(current_df.columns))
        with col3:
            st.metric("Missing Values", current_df.isnull().sum().sum())
        with col4:
            st.metric("Memory Usage", f"{current_df.memory_usage(deep=True).sum() / 1024:.2f} KB")
        
        # Data preview
        st.subheader("🔍 Data Preview")
        st.dataframe(current_df.head(10), use_container_width=True)
        
        # Create tabs for different functionalities (AI removed for keyless use)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧹 Data Cleaning", "💬 Query Data", "📊 Visualizations", "🧪 EDA Report", "📤 Export"])
        
        with tab1:
            st.subheader("🧹 Professional Data Cleaning")
            
            # Data cleaning walkthrough for new users
            if df.isnull().sum().sum() > 0 or len(df[df.duplicated()]) > 0:
                st.warning("⚠️ Data quality issues detected! Let's clean your data step by step.")
                
                with st.expander("📚 How to Clean Your Data (Step-by-Step Guide)", expanded=True):
                    st.markdown("""
                    ### 🎯 Quick Start Guide for Data Cleaning
                    
                    **Step 1:** Click "🔍 Analyze Data Quality" to see what needs fixing
                    **Step 2:** Review the quality score and detailed analysis  
                    **Step 3:** Click "💡 Get Cleaning Suggestions" for recommendations
                    **Step 4:** Select cleaning operations and click "🧹 Auto-Clean Data"
                    **Step 5:** Click "✅ Use Cleaned Data" to apply changes
                    
                    Your original data is always preserved - you can reset anytime!
                    """)
            
            # Initialize data cleaner
            cleaner = data_cleaning.DataCleaner(current_df if 'current_df' in locals() else df)
            
            # Data Quality Dashboard
            st.markdown("### 📊 Data Quality Assessment")
            
            if st.button("🔍 Analyze Data Quality", type="primary"):
                with st.spinner("Analyzing data quality..."):
                    quality_report = cleaner.generate_data_quality_report()
                
                # Display quality score prominently
                score = quality_report['quality_score']
                score_color = "green" if score >= 80 else "orange" if score >= 60 else "red"
                st.markdown(f"### Overall Quality Score: <span style='color: {score_color}'>{score}/100</span>", unsafe_allow_html=True)
                
                # Quality metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Missing Values", 
                        quality_report['missing_data']['total_missing'],
                        delta=f"{quality_report['missing_data']['columns_with_missing']} columns affected"
                    )
                
                with col2:
                    st.metric(
                        "Duplicate Rows", 
                        quality_report['duplicates']['total_duplicates'],
                        delta=f"{quality_report['duplicates']['percentage']}%"
                    )
                
                with col3:
                    outlier_count = sum(info['iqr_outliers'] for info in quality_report['outliers'].values())
                    st.metric("Outliers Detected", outlier_count)
                
                with col4:
                    memory_mb = quality_report['dataset_info']['memory_usage_mb']
                    st.metric("Memory Usage", f"{memory_mb} MB")
                
                # Detailed quality analysis
                st.markdown("### 📋 Detailed Quality Analysis")
                
                # Missing data analysis
                if quality_report['missing_data']['total_missing'] > 0:
                    with st.expander("🔍 Missing Data Analysis", expanded=True):
                        missing_df = pd.DataFrame([
                            {
                                'Column': col, 
                                'Missing Count': info['count'],
                                'Missing %': info['percentage'],
                                'Pattern': info['pattern'],
                                'Severity': quality_report['missing_data']['severity']
                            }
                            for col, info in quality_report['missing_data']['patterns'].items()
                        ])
                        st.dataframe(missing_df, use_container_width=True)
                
                # Outlier analysis
                if quality_report['outliers']:
                    with st.expander("📈 Outlier Analysis"):
                        outlier_df = pd.DataFrame([
                            {
                                'Column': col,
                                'IQR Outliers': info['iqr_outliers'],
                                'Z-Score Outliers': info['z_score_outliers'],
                                'Lower Bound': info['iqr_bounds']['lower'],
                                'Upper Bound': info['iqr_bounds']['upper'],
                                'Severity': info['severity']
                            }
                            for col, info in quality_report['outliers'].items()
                        ])
                        st.dataframe(outlier_df, use_container_width=True)
                
                # Data type recommendations
                with st.expander("🔧 Data Type Optimization"):
                    type_df = pd.DataFrame([
                        {
                            'Column': col,
                            'Current Type': info['current_type'],
                            'Suggested Type': info['suggested_type'],
                            'Memory (bytes)': info['memory_usage_bytes'],
                            'Needs Optimization': info['optimization_possible']
                        }
                        for col, info in quality_report['data_types'].items()
                    ])
                    st.dataframe(type_df, use_container_width=True)
            
            # Cleaning Strategies
            st.markdown("### 🛠️ Cleaning Strategies")
            
            if st.button("💡 Get Cleaning Suggestions", type="secondary"):
                with st.spinner("Generating cleaning recommendations..."):
                    suggestions = cleaner.suggest_cleaning_strategies()
                
                for category, suggestion_list in suggestions.items():
                    if suggestion_list:
                        st.markdown(f"**{category.replace('_', ' ').title()}:**")
                        for suggestion in suggestion_list:
                            st.write(f"• {suggestion}")
                        st.write("")
            
            # Auto-Cleaning Options
            st.markdown("### 🤖 Automated Cleaning")
            
            cleaning_options = st.multiselect(
                "Select cleaning operations:",
                options=[
                    "remove_duplicates",
                    "fix_data_types", 
                    "handle_missing_basic",
                    "clean_text",
                    "remove_outliers"
                ],
                default=["remove_duplicates", "fix_data_types", "handle_missing_basic"],
                help="Choose which automated cleaning operations to apply"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🧹 Auto-Clean Data", type="primary"):
                    if cleaning_options:
                        with st.spinner("Applying cleaning operations..."):
                            try:
                                cleaned_df = cleaner.auto_clean_data(cleaning_options)
                                cleaning_summary = cleaner.get_cleaning_summary()
                                
                                # Store cleaned data and summary in session state
                                st.session_state['temp_cleaned_data'] = cleaned_df
                                st.session_state['cleaning_summary'] = cleaning_summary
                                st.session_state['show_cleaning_results'] = True
                                
                            except Exception as e:
                                st.error(f"Error during cleaning: {str(e)}")
                                st.session_state['show_cleaning_results'] = False
                    else:
                        st.warning("Please select at least one cleaning operation")
            
            # Show cleaning results if available
            if st.session_state.get('show_cleaning_results', False) and 'temp_cleaned_data' in st.session_state:
                st.success("Data cleaning completed!")
                
                cleaning_summary = st.session_state['cleaning_summary']
                
                # Show cleaning summary
                st.markdown("#### 📊 Cleaning Summary")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric("Original Rows", cleaning_summary['original_shape'][0])
                    st.metric("Cleaned Rows", cleaning_summary['current_shape'][0])
                
                with col_b:
                    st.metric("Rows Removed", cleaning_summary['rows_changed'])
                    memory_savings = cleaning_summary['memory_optimization']
                    st.metric("Memory Saved", f"{memory_savings['savings_mb']} MB")
                
                # Show cleaning operations performed
                with st.expander("🔍 Operations Performed"):
                    for operation in cleaning_summary['cleaning_log']:
                        st.write(f"• {operation}")
                
                # Buttons for applying or discarding cleaned data
                col_apply, col_reset = st.columns(2)
                
                with col_apply:
                    if st.button("✅ Use Cleaned Data", type="primary"):
                        st.session_state['cleaned_data'] = st.session_state['temp_cleaned_data']
                        st.session_state['show_cleaning_results'] = False
                        # Clean up temporary data
                        if 'temp_cleaned_data' in st.session_state:
                            del st.session_state['temp_cleaned_data']
                        if 'cleaning_summary' in st.session_state:
                            del st.session_state['cleaning_summary']
                        st.success("Cleaned data is now being used for analysis!")
                        st.rerun()
                
                with col_reset:
                    if st.button("🔄 Reset to Original", type="secondary"):
                        # Remove cleaned data and show original
                        if 'cleaned_data' in st.session_state:
                            del st.session_state['cleaned_data']
                        st.session_state['show_cleaning_results'] = False
                        # Clean up temporary data
                        if 'temp_cleaned_data' in st.session_state:
                            del st.session_state['temp_cleaned_data']
                        if 'cleaning_summary' in st.session_state:
                            del st.session_state['cleaning_summary']
                        st.success("Reset to original data!")
                        st.rerun()
                    else:
                        st.warning("Please select at least one cleaning operation")
            
            with col2:
                if st.button("🔄 Reset to Original Data"):
                    if 'cleaned_data' in st.session_state:
                        del st.session_state['cleaned_data']
                        st.success("Reset to original data")
                        st.rerun()
            
            # Advanced Cleaning Options
            with st.expander("🔬 Advanced Cleaning Options"):
                st.markdown("#### Custom Missing Value Handling")
                
                missing_strategy = st.selectbox(
                    "Missing value strategy:",
                    ["Drop rows", "Fill with mean/median", "Fill with mode", "Forward fill", "Backward fill", "Custom value"]
                )
                
                if missing_strategy == "Custom value":
                    custom_fill = st.text_input("Custom fill value:", "Unknown")
                
                st.markdown("#### Outlier Treatment")
                outlier_method = st.selectbox(
                    "Outlier handling:",
                    ["Remove outliers", "Cap outliers", "Log transformation", "Keep outliers"]
                )
                
                if outlier_method == "Cap outliers":
                    percentile = st.slider("Cap at percentile:", 90, 99, 95)
                
                st.markdown("#### Text Cleaning Options")
                text_options = st.multiselect(
                    "Text cleaning operations:",
                    ["Remove special characters", "Convert to lowercase", "Remove extra spaces", "Remove leading/trailing spaces"]
                )
            
            # Data Validation
            st.markdown("### ✅ Data Validation")
            
            if st.button("🔍 Validate Data Quality"):
                # Use cleaned data if available, otherwise original
                validation_df = st.session_state.get('cleaned_data', df)
                validator = data_cleaning.DataCleaner(validation_df)
                validation_report = validator.generate_data_quality_report()
                
                st.markdown("#### Validation Results")
                
                # Show improvements if cleaned data exists
                if 'cleaned_data' in st.session_state:
                    original_cleaner = data_cleaning.DataCleaner(df)
                    original_report = original_cleaner.generate_data_quality_report()
                    
                    improvement_col1, improvement_col2 = st.columns(2)
                    
                    with improvement_col1:
                        st.metric("Original Quality Score", f"{original_report['quality_score']}/100")
                        st.metric("Original Missing Values", original_report['missing_data']['total_missing'])
                    
                    with improvement_col2:
                        st.metric(
                            "Current Quality Score", 
                            f"{validation_report['quality_score']}/100",
                            delta=f"{validation_report['quality_score'] - original_report['quality_score']:.1f}"
                        )
                        st.metric(
                            "Current Missing Values", 
                            validation_report['missing_data']['total_missing'],
                            delta=validation_report['missing_data']['total_missing'] - original_report['missing_data']['total_missing']
                        )
                
                # Quality checklist
                checks = []
                if validation_report['missing_data']['total_missing'] == 0:
                    checks.append("✅ No missing values")
                else:
                    checks.append(f"⚠️ {validation_report['missing_data']['total_missing']} missing values remain")
                
                if validation_report['duplicates']['total_duplicates'] == 0:
                    checks.append("✅ No duplicate rows")
                else:
                    checks.append(f"⚠️ {validation_report['duplicates']['total_duplicates']} duplicate rows remain")
                
                outlier_count = sum(info['iqr_outliers'] for info in validation_report['outliers'].values())
                if outlier_count == 0:
                    checks.append("✅ No outliers detected")
                else:
                    checks.append(f"⚠️ {outlier_count} outliers detected")
                
                for check in checks:
                    st.write(check)

        with tab2:
            st.subheader("Natural Language Querying")
            st.info("💡 Ask questions about your data in plain English")
            
            # Query examples
            with st.expander("📝 Example queries"):
                st.markdown("""
                - "Show me null values"
                - "What are the data types?"
                - "Give me basic statistics"
                - "Show correlation between columns"
                - "What are the unique values in column X?"
                """)
            
            query = st.text_input(
                "💬 Ask about your data:",
                placeholder="e.g., 'Show null values' or 'What are the data types?'"
            )
            
            if query:
                with st.spinner("Processing your query..."):
                    try:
                        response = query_parser.handle_query(df, query)
                        st.success("🔍 Query Result:")
                        
                        if isinstance(response, pd.DataFrame):
                            st.dataframe(response, use_container_width=True)
                        else:
                            st.write(response)
                    except Exception as e:
                        st.error(f"❌ Error processing query: {str(e)}")
        
        with tab3:
            st.subheader("Data Visualizations")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Chart type selection with more options
                chart_type = st.selectbox(
                    "Select chart type:",
                    [
                        "Auto (Best for Data)",
                        "Line Chart",
                        "Bar Chart",
                        "Histogram",
                        "Scatter Plot",
                        "Box Plot",
                        "Pie Chart",
                        "Violin Plot",
                        "Heatmap (Correlation)",
                        "Area Chart",
                        "Density Plot",
                        "KDE Plot"
                    ]
                )
            
            # Get column options
            numeric_cols = current_df.select_dtypes(include=[np.number]).columns.tolist()
            all_cols = current_df.columns.tolist()
            
            # Determine if chart needs X and Y selection
            needs_xy_selection = chart_type in ["Scatter Plot", "Area Chart", "Line Chart"]
            needs_single_column = chart_type in ["Histogram", "Box Plot", "Pie Chart", "Violin Plot", "Density Plot", "KDE Plot"]
            
            # Column selection with intelligent UI
            if needs_xy_selection and len(numeric_cols) >= 2:
                with col2:
                    selected_x_col = st.selectbox(
                        "X-Axis Column:",
                        numeric_cols,
                        index=0
                    )
                with col3:
                    selected_y_col = st.selectbox(
                        "Y-Axis Column:",
                        numeric_cols,
                        index=min(1, len(numeric_cols)-1)
                    )
                selected_col = selected_x_col
            elif needs_single_column and numeric_cols:
                with col2:
                    selected_col = st.selectbox(
                        "Select column to visualize:",
                        numeric_cols
                    )
                selected_x_col = None
                selected_y_col = None
            elif numeric_cols:
                with col2:
                    selected_col = st.selectbox(
                        "Select column to visualize:",
                        numeric_cols
                    )
                selected_x_col = None
                selected_y_col = None
            else:
                selected_col = None
                selected_x_col = None
                selected_y_col = None
            
            if st.button("📊 Generate Visualization", type="primary", use_container_width=True):
                with st.spinner("Creating visualization..."):
                    try:
                        import matplotlib.pyplot as plt
                        import seaborn as sns
                        
                        fig, ax = plt.subplots(figsize=(12, 6))
                        
                        # Auto detection
                        if chart_type == "Auto (Best for Data)":
                            if len(current_df.select_dtypes(include=[np.number]).columns) > 1:
                                # Multiple numeric columns - correlation heatmap
                                numeric_data = current_df.select_dtypes(include=[np.number])
                                sns.heatmap(numeric_data.corr(), annot=True, cmap='coolwarm', center=0, ax=ax, cbar_kws={'label': 'Correlation'})
                                ax.set_title('Correlation Matrix Heatmap', fontsize=14, fontweight='bold')
                            elif selected_col:
                                # Single column - histogram
                                ax.hist(current_df[selected_col].dropna(), bins=30, color='steelblue', edgecolor='black', alpha=0.7)
                                ax.set_xlabel(selected_col, fontsize=11)
                                ax.set_ylabel('Frequency', fontsize=11)
                                ax.set_title(f'Distribution of {selected_col}', fontsize=14, fontweight='bold')
                                ax.grid(axis='y', alpha=0.3)
                        
                        # Line Chart
                        elif chart_type == "Line Chart":
                            if selected_x_col and selected_y_col:
                                # X and Y columns provided
                                ax.plot(current_df[selected_x_col], current_df[selected_y_col], linewidth=2, color='#2E86AB', marker='o', markersize=4, alpha=0.7)
                                ax.set_xlabel(selected_x_col, fontsize=11)
                                ax.set_ylabel(selected_y_col, fontsize=11)
                                ax.set_title(f'Line Chart: {selected_y_col} vs {selected_x_col}', fontsize=14, fontweight='bold')
                            elif selected_col:
                                # Single column - use index
                                data = current_df[selected_col].dropna()
                                ax.plot(range(len(data)), data, linewidth=2, color='#2E86AB', marker='o', markersize=4, alpha=0.7)
                                ax.set_xlabel('Index', fontsize=11)
                                ax.set_ylabel(selected_col, fontsize=11)
                                ax.set_title(f'Line Chart: {selected_col}', fontsize=14, fontweight='bold')
                            ax.grid(True, alpha=0.3)
                        
                        # Bar Chart
                        elif chart_type == "Bar Chart":
                            if selected_col:
                                data = current_df[selected_col].value_counts().head(20)
                                ax.bar(range(len(data)), data.values, color='#A23B72', alpha=0.8, edgecolor='black')
                                ax.set_xticks(range(len(data)))
                                ax.set_xticklabels(data.index, rotation=45, ha='right')
                                ax.set_ylabel('Count', fontsize=11)
                                ax.set_title(f'Bar Chart: {selected_col}', fontsize=14, fontweight='bold')
                                ax.grid(axis='y', alpha=0.3)
                        
                        # Histogram
                        elif chart_type == "Histogram":
                            if selected_col:
                                ax.hist(current_df[selected_col].dropna(), bins=40, color='#F18F01', edgecolor='black', alpha=0.7)
                                ax.set_xlabel(selected_col, fontsize=11)
                                ax.set_ylabel('Frequency', fontsize=11)
                                ax.set_title(f'Histogram: {selected_col}', fontsize=14, fontweight='bold')
                                ax.grid(axis='y', alpha=0.3)
                        
                        # Scatter Plot
                        elif chart_type == "Scatter Plot":
                            if selected_x_col and selected_y_col:
                                ax.scatter(current_df[selected_x_col], current_df[selected_y_col], alpha=0.6, s=50, color='#C73E1D')
                                ax.set_xlabel(selected_x_col, fontsize=11)
                                ax.set_ylabel(selected_y_col, fontsize=11)
                                ax.set_title(f'Scatter Plot: {selected_y_col} vs {selected_x_col}', fontsize=14, fontweight='bold')
                            else:
                                st.warning("⚠️ Scatter plot requires X and Y axis selection")
                            ax.grid(True, alpha=0.3)
                        
                        # Box Plot
                        elif chart_type == "Box Plot":
                            if selected_col:
                                ax.boxplot(current_df[selected_col].dropna(), vert=True)
                                ax.set_ylabel(selected_col, fontsize=11)
                                ax.set_title(f'Box Plot: {selected_col}', fontsize=14, fontweight='bold')
                                ax.grid(axis='y', alpha=0.3)
                        
                        # Pie Chart
                        elif chart_type == "Pie Chart":
                            if selected_col:
                                data = current_df[selected_col].value_counts().head(10)
                                colors = plt.cm.Set3(range(len(data)))
                                ax.pie(data.values, labels=data.index, autopct='%1.1f%%', colors=colors, startangle=90)
                                ax.set_title(f'Pie Chart: {selected_col}', fontsize=14, fontweight='bold')
                                ax.axis('equal')
                        
                        # Violin Plot
                        elif chart_type == "Violin Plot":
                            if selected_col:
                                parts = ax.violinplot([current_df[selected_col].dropna()], vert=True, showmeans=True, showmedians=True)
                                ax.set_ylabel(selected_col, fontsize=11)
                                ax.set_title(f'Violin Plot: {selected_col}', fontsize=14, fontweight='bold')
                                ax.grid(axis='y', alpha=0.3)
                        
                        # Heatmap (Correlation)
                        elif chart_type == "Heatmap (Correlation)":
                            numeric_data = current_df.select_dtypes(include=[np.number])
                            if len(numeric_data.columns) > 1:
                                sns.heatmap(numeric_data.corr(), annot=True, cmap='coolwarm', center=0, ax=ax, 
                                           cbar_kws={'label': 'Correlation'}, fmt='.2f')
                                ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
                            else:
                                st.warning("⚠️ Need at least 2 numeric columns for correlation heatmap")
                        
                        # Area Chart
                        elif chart_type == "Area Chart":
                            if selected_x_col and selected_y_col:
                                ax.fill_between(range(len(current_df)), current_df[selected_y_col].values, alpha=0.5, color='#06A77D')
                                ax.plot(range(len(current_df)), current_df[selected_y_col].values, linewidth=2, color='#06A77D')
                                ax.set_xlabel(selected_x_col, fontsize=11)
                                ax.set_ylabel(selected_y_col, fontsize=11)
                                ax.set_title(f'Area Chart: {selected_y_col}', fontsize=14, fontweight='bold')
                            elif selected_col:
                                data = current_df[selected_col].dropna()
                                ax.fill_between(range(len(data)), data.values, alpha=0.5, color='#06A77D')
                                ax.plot(range(len(data)), data.values, linewidth=2, color='#06A77D')
                                ax.set_xlabel('Index', fontsize=11)
                                ax.set_ylabel(selected_col, fontsize=11)
                                ax.set_title(f'Area Chart: {selected_col}', fontsize=14, fontweight='bold')
                            ax.grid(True, alpha=0.3)
                        
                        # Density Plot
                        elif chart_type == "Density Plot":
                            if selected_col:
                                current_df[selected_col].dropna().plot(kind='density', ax=ax, color='#D62828', linewidth=2)
                                ax.set_xlabel(selected_col, fontsize=11)
                                ax.set_title(f'Density Plot: {selected_col}', fontsize=14, fontweight='bold')
                                ax.grid(True, alpha=0.3)
                                ax.fill_between(ax.get_lines()[0].get_xdata(), ax.get_lines()[0].get_ydata(), alpha=0.3, color='#D62828')
                        
                        # KDE Plot
                        elif chart_type == "KDE Plot":
                            if selected_col:
                                sns.kdeplot(data=current_df, x=selected_col, ax=ax, fill=True, color='#9D4EDD', linewidth=2)
                                ax.set_title(f'KDE Plot: {selected_col}', fontsize=14, fontweight='bold')
                                ax.grid(True, alpha=0.3)
                        
                        plt.tight_layout()
                        st.pyplot(fig, use_container_width=True)
                        st.success("✅ Visualization generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating chart: {str(e)}")
                        st.info("💡 Try selecting different columns or chart type")
            
            # Chart insights
            st.markdown("---")
            st.markdown("### 📊 Chart Tips")
            st.info("""
            - **Auto**: Automatically selects the best visualization for your data
            - **Line Chart**: Best for time series or sequential data
            - **Histogram**: Shows distribution of a single variable
            - **Box Plot**: Shows outliers and quartiles
            - **Heatmap**: Shows correlations between multiple numeric columns
            - **Pie Chart**: Shows proportions of categories
            """)

        
        with tab4:
            st.subheader("Exploratory Data Analysis")
            if st.button("🚀 Generate EDA Report", type="primary"):
                with st.spinner("Generating comprehensive EDA report..."):
                    eda.show_eda(current_df)

        with tab5:
            st.subheader("📤 Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Data Export")
                
                # Export current data (cleaned if available)
                export_df = st.session_state.get('cleaned_data', current_df)
                
                if st.button("📄 Export as CSV", type="secondary"):
                    exporter = export.DataExporter(export_df)
                    csv_data = exporter.export_csv()
                    if csv_data:
                        filename = "cleaned_data_export.csv" if 'cleaned_data' in st.session_state else "data_export.csv"
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=csv_data,
                            file_name=filename,
                            mime="text/csv"
                        )
                
                if st.button("📊 Export as Excel", type="secondary"):
                    exporter = export.DataExporter(export_df)
                    excel_data = exporter.export_excel()
                    if excel_data:
                        filename = "cleaned_data_export.xlsx" if 'cleaned_data' in st.session_state else "data_export.xlsx"
                        st.download_button(
                            label="⬇️ Download Excel",
                            data=excel_data,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            
            with col2:
                st.markdown("### 📋 Report Export")
                
                if st.button("📑 Generate PDF Report", type="primary"):
                    with st.spinner("Generating PDF report..."):
                        try:
                            exporter = export.DataExporter(df)
                            pdf_data = exporter.generate_pdf_report()
                            if pdf_data:
                                st.success("✅ PDF report generated successfully!")
                                st.download_button(
                                    label="⬇️ Download PDF Report",
                                    data=pdf_data,
                                    file_name="data_analysis_report.pdf",
                                    mime="application/pdf"
                                )
                            else:
                                st.error("❌ Failed to generate PDF report")
                        except Exception as e:
                            st.error(f"❌ Error generating PDF: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ An error occurred while processing your data: {str(e)}")
        st.info("Please check your data format and try again")

else:
    # Welcome screen
    st.info("👆 Upload a CSV file or click 'Load Demo Dataset' in the sidebar to get started")
    
    st.markdown("""
    ## 🚀 Welcome to AnalytixPro
    
    Your powerful data analysis assistant! Here's what you can do:
    
    ### ✨ Key Features
    - **🧪 Automated EDA**: Get comprehensive exploratory data analysis
    - **💬 Natural Language Queries**: Ask questions about your data in plain English  
    - **📊 Smart Visualizations**: Auto-generated charts and graphs
    - **📤 Export Options**: Download reports as PDF, CSV, or Excel
    
    ### 🎯 Getting Started
    1. **Upload your CSV file** using the sidebar
    2. **Or try our demo dataset** to explore all features
    3. **Navigate through tabs** to explore different analysis options
    4. **Clean and export** your data when ready
    
    ### 💡 Example Use Cases
    - **Business Analytics**: Sales data, customer metrics, KPIs
    - **Research Data**: Survey results, experimental data, statistics
    - **Financial Analysis**: Investment data, budget tracking, performance
    - **HR Analytics**: Employee data, recruitment metrics, performance
    """)
