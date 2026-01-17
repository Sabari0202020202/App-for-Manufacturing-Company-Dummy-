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
            "2. Master Budget (End-to-End)", 
            "3. ABC Costing", 
            "4. Transfer Pricing"
        ]
    )
    
    st.markdown("---")
    st.subheader("Developer Details")
    st.markdown("**Name:** Sabarimayurnath U")
    st.markdown("MBA Finance, NMIMS Bengaluru")
    st.link_button("View LinkedIn Profile", "https://www.linkedin.com/in/sabarimayurnath-u/", type="primary")

# --- HELPER FUNCTIONS ---
def provide_template(df, filename):
    csv = df.to_csv(index=False)
    st.download_button(label=f"Download {filename} Template", data=csv, file_name=f"{filename}.csv", mime='text/csv')

def clean_currency_columns(df, numeric_cols):
    """Removes '$' and ',' from specific columns and converts to float."""
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# ==========================================
# MODULE 1: CVP ANALYSIS
# ==========================================
if selected_module == "1. CVP Analysis":
    st.title("CVP Analysis & Decision Making")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Step 1: Get Template")
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
            df = clean_currency_columns(df, ['Sales_Price', 'Variable_Cost', 'Fixed_Cost'])
            
            df['Contribution'] = df['Sales_Price'] - df['Variable_Cost']
            df['PV_Ratio_Percent'] = (df['Contribution'] / df['Sales_Price']) * 100
            df['BEP_Units'] = df['Fixed_Cost'] / df['Contribution']
            
            st.divider()
            st.dataframe(df.style.format({"Sales_Price": "${:,.2f}", "Contribution": "${:,.2f}", "PV_Ratio_Percent": "{:.1f}%"}))
            
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(px.bar(df, x='Product', y='BEP_Units', title="Break-Even Units"), use_container_width=True)
            with c2: st.plotly_chart(px.scatter(df, x='Sales_Price', y='PV_Ratio_Percent', size='Contribution', color='Product', title="Profitability Bubble Chart"), use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# MODULE 2: MASTER BUDGET (END-TO-END)
# ==========================================
elif selected_module == "2. Master Budget (End-to-End)":
    st.title("Master Budgeting System")
    st.markdown("Workflow: **Sales \u2192 Production \u2192 Materials \u2192 Labor \u2192 Overheads**")

    # The New Tab Structure
    tabs = st.tabs([
        "1. Sales Budget (Revenue & Cash)", 
        "2. Production Budget", 
        "3. Purchase Budget", 
        "4. Labor & Overheads",
        "5. Master Summary"
    ])

    # ---------------------------------------------------------
    # STEP 1: SALES BUDGET (DYNAMIC LAG LOGIC)
    # ---------------------------------------------------------
    with tabs[0]:
        st.subheader("Step 1: Sales Forecast & Collections")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("#### A. Upload Forecast")
            template_sales = pd.DataFrame({
                "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
                "Product": ["Widget A"] * 8,
                "Sales_Units": [1000, 1200, 1500, 1300, 1600, 1800, 2000, 2200],
                "Selling_Price": [50] * 8
            })
            provide_template(template_sales, "sales_forecast_template")
            uploaded_sales = st.file_uploader("Upload Sales Forecast", key="sales_up")

        with c2:
            st.markdown("#### B. Collection Logic")
            st.info("Define how you collect money.")
            
            # 1. Immediate Cash Input
            cash_pct = st.slider("% Cash Sales (Immediate)", 0, 100, 20)
            st.write(f"**Credit Balance to Collect:** {100 - cash_pct}%")
            
            # 2. Dynamic Credit Terms (Pop-up Logic)
            credit_config = [] # Will store dictionaries like {'lag': 1, 'pct': 50}
            
            if cash_pct < 100:
                st.markdown("---")
                st.markdown("**Credit Collection Schedule**")
                
                # Initialize Session State for Number of Lags
                if 'num_lags' not in st.session_state:
                    st.session_state['num_lags'] = 1
                
                # Buttons to Add/Remove Months
                col_btn1, col_btn2 = st.columns([1, 1])
                if col_btn1.button("➕ Add Month"):
                    st.session_state['num_lags'] += 1
                if col_btn2.button("➖ Remove") and st.session_state['num_lags'] > 1:
                    st.session_state['num_lags'] -= 1

                # Render Dynamic Inputs
                current_sum = cash_pct
                for i in range(1, st.session_state['num_lags'] + 1):
                    val = st.number_input(f"% Collected {i} Month(s) Later", min_value=0, max_value=100, value=0, key=f"lag_input_{i}")
                    credit_config.append({'month_lag': i, 'pct': val})
                    current_sum += val
                
                # Validation
                if current_sum < 100:
                    st.warning(f"⚠️ Total = {current_sum}%. You have {100 - current_sum}% Uncollected (Bad Debt).")
                elif current_sum > 100:
                    st.error(f"⛔ Total = {current_sum}%. Total cannot exceed 100%.")
                else:
                    st.success("✅ Total allocation is 100%.")

        if uploaded_sales:
            df_sales = pd.read_csv(uploaded_sales) if uploaded_sales.name.endswith('.csv') else pd.read_excel(uploaded_sales)
            df_sales = clean_currency_columns(df_sales, ['Sales_Units', 'Selling_Price'])
            
            # 1. Calc Revenue
            df_sales['Total_Revenue'] = df_sales['Sales_Units'] * df_sales['Selling_Price']
            
            # 2. Calc Collections (Dynamic Loop)
            monthly_rev = df_sales.groupby('Month', sort=False)['Total_Revenue'].sum().reset_index()
            
            # A. Immediate Cash
            monthly_rev['Cash_Inflow_Immediate'] = monthly_rev['Total_Revenue'] * (cash_pct / 100)
            
            # B. Dynamic Loop
            total_collected_col = monthly_rev['Cash_Inflow_Immediate'].copy()
            
            for item in credit_config:
                lag = item['month_lag']
                pct = item['pct']
                col_name = f"Collection_M{lag}"
                
                # Shift Revenue by Lag Months * Percent
                monthly_rev[col_name] = monthly_rev['Total_Revenue'].shift(lag).fillna(0) * (pct / 100)
                total_collected_col += monthly_rev[col_name]
            
            monthly_rev['Total_Cash_Collected'] = total_collected_col
            
            st.session_state['df_sales'] = df_sales
            st.session_state['df_collections'] = monthly_rev
            
            st.success("Sales Budget Generated!")
            
            st.write("### Cash Collection Schedule")
            
            # --- THE FIX IS HERE ---
            # Instead of formatting EVERYTHING, we only format the numbers
            numeric_cols = monthly_rev.select_dtypes(include=['float', 'int']).columns
            format_dict = {col: "${:,.2f}" for col in numeric_cols}
            st.dataframe(monthly_rev.style.format(format_dict))
            # -----------------------
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=monthly_rev['Month'], y=monthly_rev['Total_Revenue'], name='Revenue Booked'))
            fig.add_trace(go.Scatter(x=monthly_rev['Month'], y=monthly_rev['Total_Cash_Collected'], name='Cash Collected', line=dict(color='green', width=3)))
            st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # STEP 2: PRODUCTION BUDGET
    # ---------------------------------------------------------
    with tabs[1]:
        st.subheader("Step 2: Production Schedule")
        
        if 'df_sales' not in st.session_state:
            st.warning("Please complete Step 1 (Sales Budget) first.")
        else:
            st.write("Sales Units fetched from Step 1. Please upload Inventory Targets.")
            
            template_inv = pd.DataFrame({
                "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
                "Product": ["Widget A"] * 8,
                "Opening_Stock": [100, 150, 200, 220, 250, 270, 290, 310],
                "Desired_Closing": [150, 200, 220, 250, 270, 290, 310, 330]
            })
            c1, c2 = st.columns([1, 2])
            with c1: provide_template(template_inv, "inventory_targets")
            with c2: uploaded_inv = st.file_uploader("Upload Inventory Targets", key="inv_up")
            
            if uploaded_inv:
                df_inv = pd.read_csv(uploaded_inv) if uploaded_inv.name.endswith('.csv') else pd.read_excel(uploaded_inv)
                df_inv = clean_currency_columns(df_inv, ['Opening_Stock', 'Desired_Closing'])
                
                df_prod = pd.merge(st.session_state['df_sales'], df_inv, on=['Month', 'Product'], how='left')
                df_prod['Production_Units'] = df_prod['Sales_Units'] + df_prod['Desired_Closing'] - df_prod['Opening_Stock']
                
                st.session_state['df_production'] = df_prod
                st.success("Production Calculated!")
                st.dataframe(df_prod[['Month', 'Product', 'Sales_Units', 'Opening_Stock', 'Desired_Closing', 'Production_Units']])

    # ---------------------------------------------------------
    # STEP 3: PURCHASE BUDGET
    # ---------------------------------------------------------
    with tabs[2]:
        st.subheader("Step 3: Material Purchase Budget")
        if 'df_production' in st.session_state:
            st.info("Define Bill of Materials (BOM) to calculate raw material needs.")
            
            prods = st.session_state['df_production']['Product'].unique()
            bom_data = []
            if len(prods) > 0:
                bom_data = [{"Product": p, "Material": "Steel", "Qty_Per_Unit": 2, "Cost_Per_Mat": 10} for p in prods]
            else:
                 bom_data = [{"Product": "Example", "Material": "Steel", "Qty_Per_Unit": 2, "Cost_Per_Mat": 10}]

            edited_bom = st.data_editor(pd.DataFrame(bom_data), num_rows="dynamic")
            
            if st.button("Calculate Materials"):
                df_mat = pd.merge(st.session_state['df_production'], edited_bom, on="Product", how="left")
                df_mat['Total_Mat_Needed'] = df_mat['Production_Units'] * df_mat['Qty_Per_Unit']
                df_mat['Total_Mat_Cost'] = df_mat['Total_Mat_Needed'] * df_mat['Cost_Per_Mat']
                
                st.session_state['df_materials'] = df_mat
                st.success("Purchase Budget Created!")
                st.dataframe(df_mat[['Month', 'Product', 'Material', 'Total_Mat_Cost']])
        else:
            st.warning("Complete Step 2 first.")

    # ---------------------------------------------------------
    # STEP 4: LABOR & OVERHEADS
    # ---------------------------------------------------------
    with tabs[3]:
        st.subheader("Step 4: Labor & Overhead Budget")
        if 'df_production' in st.session_state:
            c1, c2, c3 = st.columns(3)
            lab_rate = c1.number_input("Labor Cost per Unit ($)", value=15.0)
            var_oh = c2.number_input("Variable OH per Unit ($)", value=5.0)
            fix_oh = c3.number_input("Fixed OH per Month ($)", value=10000.0)
            
            if st.button("Calculate Conversion Costs"):
                df_ops = st.session_state['df_production'].copy()
                df_ops['Labor_Cost'] = df_ops['Production_Units'] * lab_rate
                df_ops['OH_Cost'] = (df_ops['Production_Units'] * var_oh) + (fix_oh / len(df_ops['Product'].unique()))
                
                st.session_state['df_ops'] = df_ops
                st.success("Conversion Costs Calculated!")
                st.dataframe(df_ops[['Month', 'Product', 'Labor_Cost', 'OH_Cost']])
        else:
            st.warning("Complete Step 2 first.")

    # ---------------------------------------------------------
    # STEP 5: MASTER SUMMARY
    # ---------------------------------------------------------
    with tabs[4]:
        st.header("Master Budget Summary")
        if all(k in st.session_state for k in ['df_materials', 'df_ops']):
            
            mat_sum = st.session_state['df_materials'].groupby(['Month', 'Product'])['Total_Mat_Cost'].sum().reset_index()
            ops_sum = st.session_state['df_ops'][['Month', 'Product', 'Labor_Cost', 'OH_Cost']]
            
            final = pd.merge(mat_sum, ops_sum, on=['Month', 'Product'])
            final['Total_Production_Cost'] = final['Total_Mat_Cost'] + final['Labor_Cost'] + final['OH_Cost']
            
            st.dataframe(final.style.format({"Total_Mat_Cost":"${:,.2f}", "Labor_Cost":"${:,.2f}", "OH_Cost":"${:,.2f}", "Total_Production_Cost":"${:,.2f}"}))
            
            fig = px.bar(final, x="Month", y=["Total_Mat_Cost", "Labor_Cost", "OH_Cost"], title="Cost Structure by Month")
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Complete previous steps to generate the Master Budget.")

# ==========================================
# PLACEHOLDERS FOR MODULE 3 & 4
# ==========================================
elif selected_module == "3. ABC Costing":
    st.title("Activity Based Costing")
    st.info("Input Cost Pools and Activity Drivers here.")
    
elif selected_module == "4. Transfer Pricing":
    st.title("Transfer Pricing")
    st.info("Compare Divisional Profits under Market Price vs Cost.")



