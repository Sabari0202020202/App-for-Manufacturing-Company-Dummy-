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
# MODULE 1: CVP ANALYSIS
# ==========================================
if selected_module == "1. CVP Analysis":
    st.title("CVP Analysis & Decision Making")
    st.info("Upload Product Sales Price, Variable Cost, and Fixed Costs.")
    
    template = pd.DataFrame({"Product": ["A", "B"], "Sales_Price": [100, 150], "Variable_Cost": [60, 90], "Fixed_Cost": [50000, 20000]})
    provide_template(template, "cvp_template")
    
    uploaded = st.file_uploader("Upload CVP Data", type=["csv", "xlsx"])
    if uploaded:
        df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
        
        # Basic Error Handling
        numeric_cols = ['Sales_Price', 'Variable_Cost', 'Fixed_Cost']
        for col in numeric_cols:
            if col in df.columns and df[col].dtype == 'object':
                 df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[$,]', '', regex=True), errors='coerce').fillna(0)

        df['Contribution'] = df['Sales_Price'] - df['Variable_Cost']
        df['BEP_Units'] = df['Fixed_Cost'] / df['Contribution']
        
        st.dataframe(df.style.format({"Sales_Price": "${:,.2f}", "Variable_Cost": "${:,.2f}", "Contribution": "${:,.2f}"}))
        st.plotly_chart(px.bar(df, x='Product', y='BEP_Units', title="Break Even Units"))

# ==========================================
# MODULE 2: MASTER BUDGETING (COMPLETE)
# ==========================================
elif selected_module == "2. Master Budgeting (Complete)":
    st.title("Master Cash Budgeting System")
    st.markdown("Generate a complete **Cash Budget** accounting for credit terms, payment lags, and non-cash items.")
    
    tab1, tab2, tab3 = st.tabs(["1. Data Input", "2. Policy Control Center", "3. Master Cash Budget"])
    
    # --- TAB 1: DATA INPUT & CLEANING ---
    with tab1:
        st.subheader("Monthly Financial Forecast")
        st.write("Please upload the raw figures.")
        
        # Robust Template (No currency symbols to prevent initial confusion)
        template_budget = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Sales_Revenue": [100000, 120000, 150000, 130000, 160000, 180000],
            "Material_Purchases": [40000, 50000, 60000, 55000, 65000, 70000],
            "Wages": [20000, 22000, 25000, 24000, 26000, 28000],
            "Mfg_Overheads": [10000, 12000, 15000, 13000, 14000, 16000],
            "Admin_Selling_Exp": [5000, 5000, 6000, 5500, 6000, 6000],
            "Tax_Paid": [0, 0, 10000, 0, 0, 0],
            "Capital_Expenditure": [0, 50000, 0, 0, 0, 0]
        })
        provide_template(template_budget, "master_budget_template")
        
        uploaded_budget = st.file_uploader("Upload Forecast", type=["csv", "xlsx"], key="budget_full")
        
        col_bal = st.columns(2)
        opening_cash = col_bal[0].number_input("Opening Cash Balance ($)", value=10000.0)
        
        if uploaded_budget:
            try:
                # 1. Load Data
                df = pd.read_csv(uploaded_budget) if uploaded_budget.name.endswith('.csv') else pd.read_excel(uploaded_budget)
                
                # 2. SAFETY LOCK: Sanitize Columns
                # Forces 'Month' to string
                if 'Month' in df.columns:
                    df['Month'] = df['Month'].astype(str)
                
                # Forces others to numbers, removing '$' and ','
                numeric_cols = ['Sales_Revenue', 'Material_Purchases', 'Wages', 
                               'Mfg_Overheads', 'Admin_Selling_Exp', 'Tax_Paid', 'Capital_Expenditure']
                
                for col in numeric_cols:
                    if col in df.columns:
                        # Clean text artifacts if present
                        if df[col].dtype == 'object':
                            df[col] = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
                        # Convert to float
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                st.session_state['budget_full_df'] = df
                st.success("Data Loaded & Cleaned Successfully. Proceed to Tab 2.")
                
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # --- TAB 2: POLICY CONTROL CENTER ---
    with tab2:
        st.header("Financial Policy Configuration")
        c1, c2, c3 = st.columns(3)
        
        # 1. SALES
        with c1:
            st.subheader("💰 Sales & Collections")
            cash_sales_pct = st.slider("Cash Sales % (Instant)", 0, 100, 20)
            credit_sales_pct = 100 - cash_sales_pct
            st.write(f"**Credit Portion:** {credit_sales_pct}%")
            
            collect_lag_1 = st.slider("% Collected Next Month", 0, 100, 60)
            collect_lag_2 = 100 - collect_lag_1
            st.caption(f"Remaining {collect_lag_2}% collected in Month 2.")

        # 2. PURCHASES
        with c2:
            st.subheader("📦 Material Purchases")
            pay_immed_pct = st.slider("% Paid Immediately", 0, 100, 10)
            
            pay_lag_1 = st.slider("% Creditors Paid Next Month", 0, 100, 50)
            pay_lag_2 = 100 - pay_lag_1
            st.caption(f"Remaining {pay_lag_2}% paid in Month 2.")

        # 3. EXPENSES
        with c3:
            st.subheader("⚙️ Overheads & Wages")
            wage_lag = st.radio("Wage Payment:", ["Same Month", "Next Month"], horizontal=True)
            
            st.write("**Manufacturing Overheads**")
            overhead_lag = st.radio("Overhead Payment:", ["Same Month", "Next Month"], horizontal=True, key="ovh_lag")
            
            st.markdown("---")
            depreciation_amt = st.number_input("Monthly Depreciation (Non-Cash)", value=2000.0)
            st.caption("Deducted from Overheads before cash calculation.")

    # --- TAB 3: MASTER BUDGET GENERATION ---
    with tab3:
        if 'budget_full_df' in st.session_state:
            df = st.session_state['budget_full_df'].copy()
            
            # === CALCULATION ENGINE ===
            # Inflows
            df['Inflow_Cash_Sales'] = df['Sales_Revenue'] * (cash_sales_pct / 100)
            credit_sales = df['Sales_Revenue'] * (credit_sales_pct / 100)
            df['Inflow_Debtors_1'] = credit_sales.shift(1).fillna(0) * (collect_lag_1 / 100)
            df['Inflow_Debtors_2'] = credit_sales.shift(2).fillna(0) * (collect_lag_2 / 100)
            df['Total_Receipts'] = df['Inflow_Cash_Sales'] + df['Inflow_Debtors_1'] + df['Inflow_Debtors_2']
            
            # Outflows
            purchase_credit = df['Material_Purchases'] * ((100 - pay_immed_pct) / 100)
            df['Outflow_Mat_Immediate'] = df['Material_Purchases'] * (pay_immed_pct / 100)
            df['Outflow_Creditors_1'] = purchase_credit.shift(1).fillna(0) * (pay_lag_1 / 100)
            df['Outflow_Creditors_2'] = purchase_credit.shift(2).fillna(0) * (pay_lag_2 / 100)
            
            df['Outflow_Wages'] = df['Wages'] if wage_lag == "Same Month" else df['Wages'].shift(1).fillna(0)
            
            cash_overheads = (df['Mfg_Overheads'] - depreciation_amt).clip(lower=0) 
            df['Outflow_Overheads'] = cash_overheads if overhead_lag == "Same Month" else cash_overheads.shift(1).fillna(0)
            
            df['Total_Payments'] = (df['Outflow_Mat_Immediate'] + df['Outflow_Creditors_1'] + 
                                    df['Outflow_Creditors_2'] + df['Outflow_Wages'] + 
                                    df['Outflow_Overheads'] + df['Admin_Selling_Exp'] + 
                                    df['Tax_Paid'] + df['Capital_Expenditure'])
            
            # Net Cash Position
            closing_balances = []
            curr_balance = opening_cash
            for _, row in df.iterrows():
                net_flow = row['Total_Receipts'] - row['Total_Payments']
                curr_balance += net_flow
                closing_balances.append(curr_balance)
            
            df['Closing_Balance'] = closing_balances
            df['Opening_Balance'] = df['Closing_Balance'].shift(1).fillna(opening_cash)
            df['Net_Flow'] = df['Total_Receipts'] - df['Total_Payments']

            # === DISPLAY SAFETY LOCK ===
            st.subheader("Master Cash Budget")
            
            # The Dictionary that prevents the Display Error
            format_dict = {
                'Opening_Balance': "${:,.2f}",
                'Total_Receipts': "${:,.2f}",
                'Total_Payments': "${:,.2f}",
                'Net_Flow': "${:,.2f}",
                'Closing_Balance': "${:,.2f}"
            }
            
            display_cols = ['Month', 'Opening_Balance', 'Total_Receipts', 'Total_Payments', 'Net_Flow', 'Closing_Balance']
            
            # We apply formatting using the dictionary, so 'Month' is ignored
            st.dataframe(df[display_cols].style.format(format_dict))
            
            # Visualization
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['Month'], y=df['Total_Receipts'], name='Receipts', marker_color='#2ca02c'))
            fig.add_trace(go.Bar(x=df['Month'], y=df['Total_Payments'], name='Payments', marker_color='#d62728'))
            fig.add_trace(go.Scatter(x=df['Month'], y=df['Closing_Balance'], name='Cash Balance', mode='lines+markers', line=dict(color='blue', width=3)))
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Awaiting Data Upload in Tab 1")

# ==========================================
# MODULE 3 & 4: PLACEHOLDERS (As Requested)
# ==========================================
elif selected_module == "3. ABC Costing":
    st.title("Activity Based Costing")
    st.info("Input Cost Pools and Activity Drivers here.")
    
elif selected_module == "4. Transfer Pricing":
    st.title("Transfer Pricing")
    st.info("Compare Divisional Profits under Market Price vs Cost.")
