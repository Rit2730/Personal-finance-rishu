import streamlit as st
import pandas as pd
import os
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Personal Finance Manager", layout="wide")

# ---------------- PREMIUM UI CSS ----------------
st.markdown("""
<style>
/* Main background */
.stApp {
    background: radial-gradient(circle at top, #6a00ff 0%, #12001f 35%, #0b0014 100%);
    color: #ffffff;
}

/* Glass cards */
.glass {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.15);
}

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.15);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a0033, #0b0014);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #8a2be2, #4b00ff);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 18px;
    font-weight: 600;
}

.stButton > button:hover {
    opacity: 0.9;
}

/* Inputs */
input, textarea, select {
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;'>💜 Personal Finance Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#d0c7ff;'>A premium, all-in-one personal finance management system</p>",
    unsafe_allow_html=True
)

# ---------------- DATA SETUP ----------------
USERS = ["All", "Ritika", "Himanshu", "Seema"]

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

FILES = {
    "income": "data/income.csv",
    "expenses": "data/expenses.csv",
    "investments": "data/investments.csv",
    "loans": "data/loans.csv"
}

SCHEMAS = {
    "income": ["Date", "Person", "Income Type", "Amount"],
    "expenses": ["Date", "Person", "Category", "Amount"],
    "investments": ["Date", "Person", "Investment Type", "Amount"],
    "loans": ["Date", "Person", "Loan Type", "Amount", "Status"]
}

def init_file(path, cols):
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)

for k in FILES:
    init_file(FILES[k], SCHEMAS[k])

income = pd.read_csv(FILES["income"])
expenses = pd.read_csv(FILES["expenses"])
investments = pd.read_csv(FILES["investments"])
loans = pd.read_csv(FILES["loans"])

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🔹 Navigation")
section = st.sidebar.selectbox(
    "",
    ["Dashboard", "Income", "Expenses", "Investments", "Loans", "Calculators"]
)

user = st.sidebar.selectbox("User", USERS)

def f(df):
    return df if user == "All" else df[df["Person"] == user]

# ================= DASHBOARD =================
if section == "Dashboard":
    inc, exp, inv, ln = f(income), f(expenses), f(investments), f(loans)

    net_worth = (
        inc["Amount"].sum()
        - exp["Amount"].sum()
        + inv["Amount"].sum()
        + ln[(ln["Loan Type"]=="Lent") & (ln["Status"]=="Open")]["Amount"].sum()
        - ln[(ln["Loan Type"]=="Borrowed") & (ln["Status"]=="Open")]["Amount"].sum()
    )

    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Income", f"₹ {inc['Amount'].sum():,.0f}")
    c2.metric("Expenses", f"₹ {exp['Amount'].sum():,.0f}")
    c3.metric("Investments", f"₹ {inv['Amount'].sum():,.0f}")
    c4.metric("Net Worth", f"₹ {net_worth:,.0f}")
    st.markdown("</div>", unsafe_allow_html=True)

    if not inc.empty:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.subheader("Income Distribution")
        st.bar_chart(inc.groupby("Income Type")["Amount"].sum())
        st.markdown("</div>", unsafe_allow_html=True)

    if not inv.empty:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.subheader("Investment Allocation")
        st.bar_chart(inv.groupby("Investment Type")["Amount"].sum())
        st.markdown("</div>", unsafe_allow_html=True)

# ================= INCOME =================
elif section == "Income":
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Add Income")

    p = st.selectbox("Person", USERS[1:])
    t = st.selectbox("Income Type", ["Salary", "Freelance", "Interest", "Bonus", "Other"])
    a = st.number_input("Amount", min_value=0.0)
    d = st.date_input("Date", date.today())

    if st.button("Save Income"):
        income.loc[len(income)] = [d, p, t, a]
        income.to_csv(FILES["income"], index=False)
        st.success("Income saved")

    st.markdown("</div>", unsafe_allow_html=True)
    st.dataframe(income)

# ================= EXPENSE =================
elif section == "Expenses":
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Add Expense")

    p = st.selectbox("Person", USERS[1:])
    c = st.text_input("Category")
    a = st.number_input("Amount", min_value=0.0)
    d = st.date_input("Date", date.today())

    if st.button("Save Expense"):
        expenses.loc[len(expenses)] = [d, p, c, a]
        expenses.to_csv(FILES["expenses"], index=False)
        st.success("Expense saved")

    st.markdown("</div>", unsafe_allow_html=True)
    st.dataframe(expenses)

# ================= INVESTMENTS =================
elif section == "Investments":
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Add Investment")

    p = st.selectbox("Person", USERS[1:])
    i = st.text_input("Investment Type (MF, ETF, FD, etc)")
    a = st.number_input("Amount", min_value=0.0)
    d = st.date_input("Date", date.today())

    if st.button("Save Investment"):
        investments.loc[len(investments)] = [d, p, i, a]
        investments.to_csv(FILES["investments"], index=False)
        st.success("Investment saved")

    st.markdown("</div>", unsafe_allow_html=True)
    st.dataframe(investments)

# ================= LOANS =================
elif section == "Loans":
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Loans")

    p = st.selectbox("Person", USERS[1:])
    t = st.selectbox("Loan Type", ["Lent", "Borrowed"])
    a = st.number_input("Amount", min_value=0.0)
    s = st.selectbox("Status", ["Open", "Closed"])
    d = st.date_input("Date", date.today())

    if st.button("Save Loan"):
        loans.loc[len(loans)] = [d, p, t, a, s]
        loans.to_csv(FILES["loans"], index=False)
        st.success("Loan saved")

    st.markdown("</div>", unsafe_allow_html=True)
    st.dataframe(loans)

# ================= CALCULATORS =================
elif section == "Calculators":
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Compound Interest Calculator")

    p = st.number_input("Principal", min_value=0.0)
    r = st.number_input("Rate (%)", min_value=0.0)
    t = st.number_input("Years", min_value=0.0)

    if st.button("Calculate"):
        fv = p * ((1 + r/100) ** t)
        st.success(f"Future Value: ₹ {fv:,.2f}")

    st.markdown("</div>", unsafe_allow_html=True)
