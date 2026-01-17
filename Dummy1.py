import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Manufacturing FinOps Suite", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Navigation")
    selected_module = st.radio(
        "Select Module:",
        [
            "1. CVP Analysis", 
            "2. Master Budgeting (Complete)", 
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

# ==========================================
# MODULE 1: CVP ANALYSIS (Standard)
# ==========================================
if selected_module == "1. CVP Analysis":
    st.title("CVP Analysis & Decision Making")
    st.info("Upload Product Sales Price, Variable Cost, and Fixed Costs.")
    
    template = pd.DataFrame({"Product": ["A", "B"], "Sales_Price": [100, 150], "Variable_Cost": [60, 90], "Fixed_Cost": [50000, 20000]})
    provide_template(template, "cvp_template")
    
    uploaded = st.file_uploader("Upload CVP Data", type=["csv", "xlsx"])
    if uploaded:
        df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
        df['Contribution'] = df['Sales_Price'] - df['Variable_Cost']
        df['BEP_Units'] = df['Fixed_Cost'] / df['Contribution']
        st.dataframe(df)
        st.plotly_chart(px.bar(df, x='Product', y='BEP_Units', title="Break Even Units"))

# ==========================================
# MODULE 2: MASTER BUDGETING (COMPLETE)
# ==========================================
elif selected_module == "2. Master Budgeting (Complete)":
    st.title("Master Cash Budgeting System")
    st.markdown("Generate a complete **Cash Budget** accounting for credit terms, payment lags, and non-cash items (Depreciation).")
    
    tab1, tab2, tab3 = st.tabs(["1. Data Input", "2. Policy Control Center", "3. Master Cash Budget"])
    
    # --- TAB 1: EXTENDED DATA INPUT ---
    # --- TAB 1: EXTENDED DATA INPUT ---
    with tab1:
        st.subheader("Monthly Financial Forecast")
        st.write("Please upload the raw figures for Sales, Purchases, and Expenses for the budget period.")
        
        # Comprehensive Template
        template_budget = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Sales_Revenue": [100000, 120000, 150000, 130000, 160000, 180000],
            "Material_Purchases": [40000, 50000, 60000, 55000, 65000, 70000],
            "Wages": [20000, 22000, 25000, 24000, 26000, 28000],
            "Mfg_Overheads": [10000, 12000, 15000, 13000, 14000, 16000],
            "Admin_Selling_Exp": [5000, 5000, 6000, 5500, 6000, 6000],
            "Tax_Paid": [0, 0, 10000, 0, 0, 0],  # Discrete event
            "Capital_Expenditure": [0, 50000, 0, 0, 0, 0] # Discrete event
        })
        provide_template(template_budget, "master_budget_template")
        
        uploaded_budget = st.file_uploader("Upload Forecast", type=["csv", "xlsx"], key="budget_full")
        
        col_bal = st.columns(2)
        opening_cash = col_bal[0].number_input("Opening Cash Balance ($)", value=10000)
        
        if uploaded_budget:
            # 1. Load Data
            df = pd.read_csv(uploaded_budget) if uploaded_budget.name.endswith('.csv') else pd.read_excel(uploaded_budget)
            
            # 2. SANITIZE DATA (The Fix)
            # This loop converts text like "10,000" into number 10000.0
            numeric_cols = ['Sales_Revenue', 'Material_Purchases', 'Wages', 
                           'Mfg_Overheads', 'Admin_Selling_Exp', 'Tax_Paid', 'Capital_Expenditure']
            
            for col in numeric_cols:
                # If the column exists, force it to be a number
                if col in df.columns:
                    # Remove '$' and ',' if they exist
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
                    # Convert to number, turn errors (text) into 0
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            st.session_state['budget_full_df'] = df
            st.success("Data Loaded and Cleaned. Go to 'Policy Control Center'.")
    # --- TAB 2: POLICY CONTROL CENTER (THE BRAIN) ---
    with tab2:
        st.header("Financial Policy Configuration")
        st.write("Configure how and when cash actually moves.")
        
        c1, c2, c3 = st.columns(3)
        
        # 1. SALES (INFLOW)
        with c1:
            st.subheader("💰 Sales & Collections")
            st.info("Logic: Debtors Collection Period")
            cash_sales_pct = st.slider("Cash Sales % (Instant)", 0, 100, 20)
            credit_sales_pct = 100 - cash_sales_pct
            st.write(f"**Credit Portion:** {credit_sales_pct}%")
            
            # Lag Logic
            collect_lag_1 = st.slider("% of Credit Collected in Next Month", 0, 100, 60)
            collect_lag_2 = 100 - collect_lag_1
            st.caption(f"Remaining {collect_lag_2}% collected in Month 2.")

        # 2. PURCHASES (OUTFLOW)
        with c2:
            st.subheader("📦 Material Purchases")
            st.info("Logic: Creditors Payment Period")
            pay_immed_pct = st.slider("% Paid Immediately (Cash Purchase)", 0, 100, 10)
            
            # Creditors Lag
            pay_lag_1 = st.slider("% Creditors Paid Next Month", 0, 100, 50)
            pay_lag_2 = 100 - pay_lag_1
            st.caption(f"Remaining {pay_lag_2}% paid in Month 2.")

        # 3. EXPENSES & OVERHEADS
        with c3:
            st.subheader("⚙️ Overheads & Wages")
            st.info("Logic: Time Lag & Non-Cash Items")
            
            # Wages
            wage_lag = st.radio("Wage Payment:", ["Same Month", "Next Month"], horizontal=True)
            
            # Overheads (Depreciation Handling)
            st.write("**Manufacturing Overheads**")
            overhead_lag = st.radio("Overhead Payment:", ["Same Month", "Next Month"], horizontal=True, key="ovh_lag")
            
            # Non-cash adjustment
            st.markdown("---")
            depreciation_amt = st.number_input("Monthly Depreciation (Non-Cash)", value=2000)
            st.caption(f"This amount will be deducted from Mfg Overheads for Cash calculation.")

    # --- TAB 3: MASTER BUDGET GENERATION ---
    with tab3:
        if 'budget_full_df' in st.session_state:
            df = st.session_state['budget_full_df'].copy()
            
            # === STEP 1: INFLOWS ===
            # Cash Sales
            df['Inflow_Cash_Sales'] = df['Sales_Revenue'] * (cash_sales_pct / 100)
            
            # Credit Collections
            credit_sales = df['Sales_Revenue'] * (credit_sales_pct / 100)
            df['Inflow_Debtors_1'] = credit_sales.shift(1).fillna(0) * (collect_lag_1 / 100)
            df['Inflow_Debtors_2'] = credit_sales.shift(2).fillna(0) * (collect_lag_2 / 100)
            
            df['Total_Receipts'] = df['Inflow_Cash_Sales'] + df['Inflow_Debtors_1'] + df['Inflow_Debtors_2']
            
            # === STEP 2: OUTFLOWS ===
            # A. Materials (Creditors)
            purchase_credit = df['Material_Purchases'] * ((100 - pay_immed_pct) / 100)
            
            df['Outflow_Materials_Immediate'] = df['Material_Purchases'] * (pay_immed_pct / 100)
            df['Outflow_Creditors_1'] = purchase_credit.shift(1).fillna(0) * (pay_lag_1 / 100)
            df['Outflow_Creditors_2'] = purchase_credit.shift(2).fillna(0) * (pay_lag_2 / 100)
            
            # B. Wages
            if wage_lag == "Same Month":
                df['Outflow_Wages'] = df['Wages']
            else:
                df['Outflow_Wages'] = df['Wages'].shift(1).fillna(0)
                
            # C. Overheads (Adjusting for Depreciation)
            # Cash Overheads = Total Overheads - Depreciation
            cash_overheads = (df['Mfg_Overheads'] - depreciation_amt).clip(lower=0) 
            
            if overhead_lag == "Same Month":
                df['Outflow_Overheads'] = cash_overheads
            else:
                df['Outflow_Overheads'] = cash_overheads.shift(1).fillna(0)
            
            # D. Admin, Tax, Capex (Assumed Same Month for simplicity, or add shift if needed)
            df['Outflow_Admin'] = df['Admin_Selling_Exp']
            df['Outflow_Tax'] = df['Tax_Paid']
            df['Outflow_Capex'] = df['Capital_Expenditure']
            
            df['Total_Payments'] = (df['Outflow_Materials_Immediate'] + df['Outflow_Creditors_1'] + 
                                    df['Outflow_Creditors_2'] + df['Outflow_Wages'] + 
                                    df['Outflow_Overheads'] + df['Outflow_Admin'] + 
                                    df['Outflow_Tax'] + df['Outflow_Capex'])
            
            # === STEP 3: NET CASH POSITION ===
            # We must calculate running balance iteratively
            closing_balances = []
            curr_balance = opening_cash
            
            for index, row in df.iterrows():
                net_flow = row['Total_Receipts'] - row['Total_Payments']
                curr_balance += net_flow
                closing_balances.append(curr_balance)
            
            df['Closing_Balance'] = closing_balances
            df['Opening_Balance'] = df['Closing_Balance'].shift(1).fillna(opening_cash)
            
            # === DISPLAY ===
            st.subheader("Master Cash Budget")
            
            # Format large numbers for readability
            display_cols = ['Month', 'Total_Receipts', 'Total_Payments', 'Net_Flow', 'Closing_Balance']
            df['Net_Flow'] = df['Total_Receipts'] - df['Total_Payments']
            
            st.dataframe(df[['Month', 'Opening_Balance', 'Total_Receipts', 'Total_Payments', 'Net_Flow', 'Closing_Balance']].style.format("${:,.2f}"))
            
            # Detailed Breakdown (Expandable)
            with st.expander("See Detailed Breakdown (Inflows & Outflows)"):
                st.write("**Receipts Detail**")
                st.dataframe(df[['Month', 'Inflow_Cash_Sales', 'Inflow_Debtors_1', 'Inflow_Debtors_2']])
                
                st.write("**Payments Detail**")
                st.dataframe(df[['Month', 'Outflow_Materials_Immediate', 'Outflow_Creditors_1', 'Outflow_Wages', 'Outflow_Overheads', 'Outflow_Tax']])

            # Visualization
            st.subheader("Cash Position Visualization")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['Month'], y=df['Total_Receipts'], name='Receipts', marker_color='green'))
            fig.add_trace(go.Bar(x=df['Month'], y=df['Total_Payments'], name='Payments', marker_color='red'))
            fig.add_trace(go.Scatter(x=df['Month'], y=df['Closing_Balance'], name='Cash Balance', mode='lines+markers', line=dict(color='blue', width=3)))
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("Please upload data in Tab 1.")

# ==========================================
# MODULE 3 & 4 (Placeholders)
# ==========================================
elif selected_module == "3. ABC Costing":
    st.title("Activity Based Costing")
    st.info("Module under construction.")
    
elif selected_module == "4. Transfer Pricing":
    st.title("Transfer Pricing")
    st.info("Module under construction.")
