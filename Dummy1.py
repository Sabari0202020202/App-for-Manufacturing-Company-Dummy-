import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Manufacturing Ops Budget", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Navigation")
    selected_module = st.radio(
        "Select Module:",
        ["1. CVP Analysis", "2. Master Budget (Operational)", "3. ABC Costing", "4. Transfer Pricing"]
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

# ==========================================
# MODULE 1: CVP ANALYSIS (Kept Simple)
# ==========================================
if selected_module == "1. CVP Analysis":
    st.title("CVP Analysis")
    st.info("Upload standard CVP inputs.")
    # (Placeholder to save space for the main request)
    st.write("Please proceed to Module 2 for the Operational Budgeting System.")

# ==========================================
# MODULE 2: OPERATIONAL MASTER BUDGET
# ==========================================
elif selected_module == "2. Master Budget (Operational)":
    st.title("Operational Master Budget")
    st.markdown("This module builds the budget sequentially: **Sales \u2192 Production \u2192 Materials \u2192 Labor \u2192 Overheads**.")

    # We use distinct tabs for the workflow steps
    tab_prod, tab_mat, tab_lab, tab_oh, tab_final = st.tabs([
        "1. Production Budget", 
        "2. Purchase (Material) Budget", 
        "3. Labor Budget",
        "4. Overhead Budget",
        "5. Final Master Budget"
    ])

    # ---------------------------------------------------------
    # STEP 1: PRODUCTION BUDGET
    # ---------------------------------------------------------
    with tab_prod:
        st.subheader("Step 1: Production Schedule")
        st.write("Determine how many units you need to manufacture.")
        
        # Template: Sales Forecast
        template_sales = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar"],
            "Product": ["Widget A", "Widget A", "Widget A"],
            "Sales_Units": [1000, 1200, 1500],
            "Opening_FG_Stock": [100, 150, 200],
            "Desired_Closing_FG": [150, 200, 250]
        })
        
        col1, col2 = st.columns([1, 2])
        with col1:
            provide_template(template_sales, "production_input_template")
            uploaded_prod = st.file_uploader("Upload Sales & Inventory Data", type=["csv", "xlsx"], key="prod_up")
        
        if uploaded_prod:
            df_prod = pd.read_csv(uploaded_prod) if uploaded_prod.name.endswith('.csv') else pd.read_excel(uploaded_prod)
            
            # LOGIC: Production = Sales + Closing - Opening
            df_prod['Production_Units'] = df_prod['Sales_Units'] + df_prod['Desired_Closing_FG'] - df_prod['Opening_FG_Stock']
            
            # Save to session for next tabs
            st.session_state['df_production'] = df_prod
            
            st.success("Production Budget Calculated!")
            st.dataframe(df_prod)
            
            # Graph
            fig_prod = px.bar(df_prod, x="Month", y="Production_Units", color="Product", barmode="group", title="Monthly Production Requirements")
            st.plotly_chart(fig_prod, use_container_width=True)

    # ---------------------------------------------------------
    # STEP 2: MATERIAL PURCHASE BUDGET (The Complex Part)
    # ---------------------------------------------------------
    with tab_mat:
        st.subheader("Step 2: Material Purchase Budget")
        
        if 'df_production' not in st.session_state:
            st.warning("Please complete Step 1 (Production Budget) first.")
        else:
            st.info("Define the Bill of Materials (BOM) to calculate raw material needs.")
            
            # A. DEFINE BOM (Recipe)
            st.markdown("**A. Bill of Materials (Recipe)**")
            st.caption("Edit the table below to add/remove Raw Materials needed for your products.")
            
            # Get unique products from Step 1
            unique_products = st.session_state['df_production']['Product'].unique()
            
            # Create a default BOM structure
            default_bom_data = []
            for p in unique_products:
                default_bom_data.append({"Product": p, "Raw_Material": "Steel (kg)", "Qty_Per_Unit": 2.0, "Cost_Per_RM": 10.0})
                default_bom_data.append({"Product": p, "Raw_Material": "Plastic (kg)", "Qty_Per_Unit": 0.5, "Cost_Per_RM": 5.0})
            
            # Allow user to Add/Subtract rows dynamically
            df_bom_input = pd.DataFrame(default_bom_data)
            edited_bom = st.data_editor(df_bom_input, num_rows="dynamic", key="bom_editor")
            
            # B. CALCULATE
            if st.button("Calculate Purchase Budget"):
                # Merge Production (Step 1) with BOM (Step 2)
                # This 'explodes' the production df: 1 Product row becomes multiple Material rows
                df_prod_copy = st.session_state['df_production'].copy()
                
                # Merge on Product name
                df_materials = pd.merge(df_prod_copy, edited_bom, on="Product", how="left")
                
                # Logic: Total RM Needed = Production Units * Qty Per Unit
                df_materials['Total_RM_Required'] = df_materials['Production_Units'] * df_materials['Qty_Per_Unit']
                df_materials['Total_Purchase_Cost'] = df_materials['Total_RM_Required'] * df_materials['Cost_Per_RM']
                
                st.session_state['df_materials'] = df_materials
                st.success("Material Requirements Calculated!")
                
                # Display Summary
                st.write("### Material Purchase Requirements")
                st.dataframe(df_materials[['Month', 'Product', 'Raw_Material', 'Total_RM_Required', 'Total_Purchase_Cost']])
                
                # Visual
                fig_mat = px.bar(df_materials, x="Month", y="Total_Purchase_Cost", color="Raw_Material", title="Material Cost Budget")
                st.plotly_chart(fig_mat, use_container_width=True)

    # ---------------------------------------------------------
    # STEP 3: LABOR BUDGET
    # ---------------------------------------------------------
    with tab_lab:
        st.subheader("Step 3: Direct Labor Budget")
        
        if 'df_production' not in st.session_state:
            st.warning("Please complete Step 1 first.")
        else:
            col1, col2 = st.columns(2)
            labor_hours = col1.number_input("Standard Labor Hours per Unit", value=2.0)
            labor_rate = col2.number_input("Labor Rate per Hour ($)", value=15.0)
            
            if st.button("Calculate Labor Budget"):
                df_labor = st.session_state['df_production'].copy()
                df_labor['Total_Labor_Hours'] = df_labor['Production_Units'] * labor_hours
                df_labor['Total_Labor_Cost'] = df_labor['Total_Labor_Hours'] * labor_rate
                
                st.session_state['df_labor'] = df_labor
                st.success("Labor Budget Calculated!")
                st.dataframe(df_labor[['Month', 'Product', 'Total_Labor_Hours', 'Total_Labor_Cost']])

    # ---------------------------------------------------------
    # STEP 4: OVERHEAD BUDGET
    # ---------------------------------------------------------
    with tab_oh:
        st.subheader("Step 4: Manufacturing Overhead Budget")
        
        if 'df_production' not in st.session_state:
            st.warning("Please complete Step 1 first.")
        else:
            col1, col2 = st.columns(2)
            var_oh_rate = col1.number_input("Variable Overhead per Unit ($)", value=5.0)
            fixed_oh_total = col2.number_input("Total Fixed Overhead per Month ($)", value=10000.0)
            
            if st.button("Calculate Overhead Budget"):
                df_oh = st.session_state['df_production'].copy()
                df_oh['Variable_OH_Cost'] = df_oh['Production_Units'] * var_oh_rate
                
                # We need to allocate fixed cost per month. 
                # Since the DF has multiple products per month, we group by month to check
                # For simplicity in this view, we just add the column
                df_oh['Fixed_OH_Allocation'] = fixed_oh_total / len(df_oh['Product'].unique()) # Simplified allocation
                
                df_oh['Total_OH_Cost'] = df_oh['Variable_OH_Cost'] + df_oh['Fixed_OH_Allocation']
                
                st.session_state['df_oh'] = df_oh
                st.success("Overhead Budget Calculated!")
                st.dataframe(df_oh[['Month', 'Product', 'Total_OH_Cost']])

    # ---------------------------------------------------------
    # STEP 5: FINAL MASTER SUMMARY
    # ---------------------------------------------------------
    with tab_final:
        st.header("Final Master Budget Summary")
        
        if all(key in st.session_state for key in ['df_materials', 'df_labor', 'df_oh']):
            # 1. Aggregating Material Costs by Month & Product
            mat_summary = st.session_state['df_materials'].groupby(['Month', 'Product'])['Total_Purchase_Cost'].sum().reset_index()
            mat_summary.rename(columns={'Total_Purchase_Cost': 'Material_Cost'}, inplace=True)
            
            # 2. Aggregating Labor
            lab_summary = st.session_state['df_labor'][['Month', 'Product', 'Total_Labor_Cost']]
            
            # 3. Aggregating Overhead
            oh_summary = st.session_state['df_oh'][['Month', 'Product', 'Total_OH_Cost']]
            
            # 4. Merging all
            df_master = pd.merge(mat_summary, lab_summary, on=['Month', 'Product'])
            df_master = pd.merge(df_master, oh_summary, on=['Month', 'Product'])
            
            df_master['Total_Production_Cost'] = df_master['Material_Cost'] + df_master['Total_Labor_Cost'] + df_master['Total_OH_Cost']
            
            st.write("### Consolidated Cost Sheet")
            
            # Formatting for display
            format_dict = {
                "Material_Cost": "${:,.2f}",
                "Total_Labor_Cost": "${:,.2f}",
                "Total_OH_Cost": "${:,.2f}",
                "Total_Production_Cost": "${:,.2f}"
            }
            st.dataframe(df_master.style.format(format_dict))
            
            # FINAL GRAPH
            st.write("### Cost Components Breakdown")
            fig_final = px.bar(
                df_master, 
                x="Month", 
                y=["Material_Cost", "Total_Labor_Cost", "Total_OH_Cost"],
                title="Total Budgeted Cost Composition",
                labels={"value": "Cost ($)", "variable": "Cost Component"}
            )
            st.plotly_chart(fig_final, use_container_width=True)
            
        else:
            st.error("Please complete Steps 1, 2, 3, and 4 to generate the Final Budget.")

# ==========================================
# PLACEHOLDERS FOR MODULE 3 & 4
# ==========================================
elif selected_module == "3. ABC Costing":
    st.title("Activity Based Costing")
    st.info("Input Cost Pools and Activity Drivers here.")
    
elif selected_module == "4. Transfer Pricing":
    st.title("Transfer Pricing")
    st.info("Compare Divisional Profits under Market Price vs Cost.")
