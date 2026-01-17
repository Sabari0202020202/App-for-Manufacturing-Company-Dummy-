import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Manufacturing Ops Suite", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Navigation")
    selected_module = st.radio(
        "Select Module:",
        [
            "1. CVP Analysis", 
            "2. Master Budget (Operational)", 
            "3. ABC Costing", 
            "4. Transfer Pricing"
        ]
    )
    
    st.markdown("---")
    st.subheader("Developer Details")
    st.markdown("**Name:** Sabarimayurnath U")
    st.markdown("MBA Finance, NMIMS Bengaluru")
    st.link_button("View LinkedIn Profile", "https://www.linkedin.com/in/sabarimayurnath-u/", type="primary")

# --- HELPER: TEMPLATE DOWNLOADER ---
def provide_template(df, filename):
    csv = df.to_csv(index=False)
    st.download_button(label=f"Download {filename} Template", data=csv, file_name=f"{filename}.csv", mime='text/csv')

# --- HELPER: DATA CLEANER (The Anti-Crash System) ---
def clean_currency_columns(df, numeric_cols):
    """Removes '$' and ',' from specific columns and converts to float."""
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# ==========================================
# MODULE 1: CVP ANALYSIS (Restored)
# ==========================================
if selected_module == "1. CVP Analysis":
    st.title("CVP Analysis & Decision Making")
    st.markdown("Calculate **Break-Even Point**, **Contribution Margin**, and **P/V Ratio**.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Step 1: Get Template")
        # Template definition
        template_cvp = pd.DataFrame({
            "Product": ["Product A", "Product B"], 
            "Sales_Price": [100, 150], 
            "Variable_Cost": [60, 90], 
            "Fixed_Cost": [50000, 20000]
        })
        provide_template(template_cvp, "cvp_template")
    
    with col2:
        st.subheader("Step 2: Upload Data")
        uploaded_cvp = st.file_uploader("Upload CVP Input", type=["csv", "xlsx"])
    
    if uploaded_cvp:
        try:
            df = pd.read_csv(uploaded_cvp) if uploaded_cvp.name.endswith('.csv') else pd.read_excel(uploaded_cvp)
            
            # Clean Data
            df = clean_currency_columns(df, ['Sales_Price', 'Variable_Cost', 'Fixed_Cost'])
            
            # Calculations
            df['Contribution'] = df['Sales_Price'] - df['Variable_Cost']
            df['PV_Ratio_Percent'] = (df['Contribution'] / df['Sales_Price']) * 100
            df['BEP_Units'] = df['Fixed_Cost'] / df['Contribution']
            
            st.divider()
            st.subheader("Analysis Results")
            
            # Display Table with Formatting
            format_dict = {
                "Sales_Price": "${:,.2f}", 
                "Variable_Cost": "${:,.2f}", 
                "Contribution": "${:,.2f}",
                "PV_Ratio_Percent": "{:.1f}%",
                "BEP_Units": "{:,.0f}"
            }
            st.dataframe(df.style.format(format_dict))
            
            # Graphs
            c1, c2 = st.columns(2)
            with c1:
                fig1 = px.bar(df, x='Product', y='BEP_Units', title="Break-Even Point (Units)", color='Product')
                st.plotly_chart(fig1, use_container_width=True)
            with c2:
                fig2 = px.scatter(df, x='Sales_Price', y='PV_Ratio_Percent', size='Contribution', 
                                  color='Product', title="Price vs Profitability (Bubble Size = Margin)")
                st.plotly_chart(fig2, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error processing file: {e}")

# ==========================================
# MODULE 2: OPERATIONAL MASTER BUDGET
# ==========================================
elif selected_module == "2. Master Budget (Operational)":
    st.title("Operational Master Budget")
    st.markdown("Workflow: **Sales \u2192 Production \u2192 Materials \u2192 Labor \u2192 Overheads**.")

    tab_prod, tab_mat, tab_lab, tab_oh, tab_final = st.tabs([
        "1. Production Budget", 
        "2. Purchase (Material) Budget", 
        "3. Labor Budget",
        "4. Overhead Budget",
        "5. Final Master Budget"
    ])

    # --- STEP 1: PRODUCTION ---
    with tab_prod:
        st.subheader("Step 1: Production Schedule")
        
        template_sales = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar"],
            "Product": ["Widget A", "Widget A", "Widget A"],
            "Sales_Units": [1000, 1200, 1500],
            "Opening_FG_Stock": [100, 150, 200],
            "Desired_Closing_FG": [150, 200, 250]
        })
        
        c1, c2 = st.columns([1, 2])
        with c1:
            provide_template(template_sales, "production_input_template")
        with c2:
            uploaded_prod = st.file_uploader("Upload Sales & Inventory Data", type=["csv", "xlsx"], key="prod_up")
        
        if uploaded_prod:
            df_prod = pd.read_csv(uploaded_prod) if uploaded_prod.name.endswith('.csv') else pd.read_excel(uploaded_prod)
            
            # Clean Data
            df_prod = clean_currency_columns(df_prod, ['Sales_Units', 'Opening_FG_Stock', 'Desired_Closing_FG'])
            
            # Logic
            df_prod['Production_Units'] = df_prod['Sales_Units'] + df_prod['Desired_Closing_FG'] - df_prod['Opening_FG_Stock']
            st.session_state['df_production'] = df_prod
            
            st.success("Production Calculated!")
            st.dataframe(df_prod)
            
            fig_prod = px.bar(df_prod, x="Month", y="Production_Units", color="Product", barmode="group", title="Monthly Production Requirements")
            st.plotly_chart(fig_prod, use_container_width=True)

    # --- STEP 2: MATERIAL PURCHASE ---
    with tab_mat:
        st.subheader("Step 2: Material Purchase Budget")
        
        if 'df_production' not in st.session_state:
            st.warning("Please complete Step 1 first.")
        else:
            st.info("Define the Bill of Materials (BOM) below.")
            
            # Dynamic BOM Editor
            unique_products = st.session_state['df_production']['Product'].unique()
            default_bom = []
            for p in unique_products:
                default_bom.append({"Product": p, "Raw_Material": "Steel", "Qty_Per_Unit": 2.0, "Cost_Per_RM": 10.0})
                default_bom.append({"Product": p, "Raw_Material": "Plastic", "Qty_Per_Unit": 0.5, "Cost_Per_RM": 5.0})
            
            edited_bom = st.data_editor(pd.DataFrame(default_bom), num_rows="dynamic", key="bom_editor")
            
            if st.button("Calculate Purchase Budget"):
                df_prod_copy = st.session_state['df_production'].copy()
                df_materials = pd.merge(df_prod_copy, edited_bom, on="Product", how="left")
                
                df_materials['Total_RM_Required'] = df_materials['Production_Units'] * df_materials['Qty_Per_Unit']
                df_materials['Total_Purchase_Cost'] = df_materials['Total_RM_Required'] * df_materials['Cost_Per_RM']
                
                st.session_state['df_materials'] = df_materials
                st.success("Materials Calculated!")
                st.dataframe(df_materials[['Month', 'Product', 'Raw_Material', 'Total_RM_Required', 'Total_Purchase_Cost']])

    # --- STEP 3: LABOR ---
    with tab_lab:
        st.subheader("Step 3: Direct Labor Budget")
        if 'df_production' in st.session_state:
            c1, c2 = st.columns(2)
            labor_hours = c1.number_input("Std Labor Hours/Unit", value=2.0)
            labor_rate = c2.number_input("Labor Rate ($/Hr)", value=15.0)
            
            if st.button("Calculate Labor"):
                df_lab = st.session_state['df_production'].copy()
                df_lab['Total_Labor_Cost'] = df_lab['Production_Units'] * labor_hours * labor_rate
                st.session_state['df_labor'] = df_lab
                st.success("Labor Calculated!")
                st.dataframe(df_lab[['Month', 'Product', 'Total_Labor_Cost']])
        else:
            st.warning("Complete Step 1 first.")

    # --- STEP 4: OVERHEAD ---
    with tab_oh:
        st.subheader("Step 4: Overhead Budget")
        if 'df_production' in st.session_state:
            c1, c2 = st.columns(2)
            var_rate = c1.number_input("Variable OH Rate ($/Unit)", value=5.0)
            fixed_total = c2.number_input("Fixed OH Total ($/Month)", value=10000.0)
            
            if st.button("Calculate Overhead"):
                df_oh = st.session_state['df_production'].copy()
                df_oh['Total_OH_Cost'] = (df_oh['Production_Units'] * var_rate) + (fixed_total / len(df_oh['Product'].unique()))
                st.session_state['df_oh'] = df_oh
                st.success("Overhead Calculated!")
                st.dataframe(df_oh[['Month', 'Product', 'Total_OH_Cost']])
        else:
            st.warning("Complete Step 1 first.")

    # --- STEP 5: SUMMARY ---
    with tab_final:
        st.header("Final Master Budget Summary")
        if all(k in st.session_state for k in ['df_materials', 'df_labor', 'df_oh']):
            # Aggregation Logic
            mat_sum = st.session_state['df_materials'].groupby(['Month', 'Product'])['Total_Purchase_Cost'].sum().reset_index()
            lab_sum = st.session_state['df_labor'][['Month', 'Product', 'Total_Labor_Cost']]
            oh_sum = st.session_state['df_oh'][['Month', 'Product', 'Total_OH_Cost']]
            
            df_final = pd.merge(mat_sum, lab_sum, on=['Month', 'Product']).merge(oh_sum, on=['Month', 'Product'])
            df_final['Total_Cost'] = df_final['Total_Purchase_Cost'] + df_final['Total_Labor_Cost'] + df_final['Total_OH_Cost']
            
            st.dataframe(df_final.style.format({"Total_Purchase_Cost":"${:,.2f}", "Total_Labor_Cost":"${:,.2f}", "Total_OH_Cost":"${:,.2f}", "Total_Cost":"${:,.2f}"}))
            
            fig = px.bar(df_final, x="Month", y=["Total_Purchase_Cost", "Total_Labor_Cost", "Total_OH_Cost"], title="Total Budget Cost Breakdown")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Complete Steps 1-4 to view the final budget.")

# ==========================================
# PLACEHOLDERS
# ==========================================
elif selected_module == "3. ABC Costing":
    st.title("Activity Based Costing")
    st.info("Input Cost Pools and Activity Drivers here.")
    
elif selected_module == "4. Transfer Pricing":
    st.title("Transfer Pricing")
    st.info("Compare Divisional Profits under Market Price vs Cost.")







