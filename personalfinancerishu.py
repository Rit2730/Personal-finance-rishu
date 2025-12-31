import streamlit as st
import pandas as pd
import os
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Personal Finance Manager", layout="wide")

# ---------------- WINE THEME (MAXIMUM SUPPORTED) ----------------
st.markdown("""
<style>
/* App background */
.stApp {
    background-color: #wine !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #3a0c17 !important;
}

/* Text */
html, body, p, h1, h2, h3, h4, h5, h6, span, div {
    color: #f5e9ec !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: rgba(255,255,255,0.12);
    padding: 18px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.25);
}

/* Buttons */
.stButton > button {
    background-color: #wine;
    color: white;
    border-radius: 10px;
    font-weight: 600;
    border: none;
}

.stButton > button:hover {
    background-color: #91264a;
}

/* Inputs */
input, textarea, select {
    background-color: rgba(255,255,255,0.10) !important;
    color: white !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    background-color: rgba(255,255,255,0.05);
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🍷 Personal Finance Management System")
st.caption("Income • Expenses • Investments • Loans • Net Worth")

# ---------------- USERS ----------------
USERS = ["All", "Ritika", "Himanshu", "Seema"]

# ---------------- DATA SETUP ----------------
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
st.sidebar.header("Navigation")
section = st.sidebar.selectbox(
    "Select Module",
    ["Dashboard", "Income", "Expenses", "Investments", "Loans", "Calculators"]
)

user = st.sidebar.selectbox("Select User", USERS)

def filter_user(df):
    if user == "All":
        return df
    return df[df["Person"] == user]

# ================= DASHBOARD =================
if section == "Dashboard":
    inc = filter_user(income)
    exp = filter_user(expenses)
    inv = filter_user(investments)
    ln = filter_user(loans)

    net_worth = (
        inc["Amount"].sum()
        - exp["Amount"].sum()
        + inv["Amount"].sum()
        + ln[(ln["Loan Type"] == "Lent") & (ln["Status"] == "Open")]["Amount"].sum()
        - ln[(ln["Loan Type"] == "Borrowed") & (ln["Status"] == "Open")]["Amount"].sum()
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Income", f"₹ {inc['Amount'].sum():,.0f}")
    c2.metric("Expenses", f"₹ {exp['Amount'].sum():,.0f}")
    c3.metric("Investments", f"₹ {inv['Amount'].sum():,.0f}")
    c4.metric("Net Worth", f"₹ {net_worth:,.0f}")

    st.divider()

    if not inc.empty:
        st.subheader("Income by Type")
        st.bar_chart(inc.groupby("Income Type")["Amount"].sum())

    if not inv.empty:
        st.subheader("Investments by Category")
        st.bar_chart(inv.groupby("Investment Type")["Amount"].sum())

# ================= INCOME =================
elif section == "Income":
    st.subheader("Add Income")

    p = st.selectbox("Person", USERS[1:])
    t = st.selectbox("Income Type", ["Salary", "Freelance", "Interest", "Bonus", "Other"])
    a = st.number_input("Amount", min_value=0.0)
    d = st.date_input("Date", date.today())

    if st.button("Save Income"):
        income.loc[len(income)] = [d, p, t, a]
        income.to_csv(FILES["income"], index=False)
        st.success("Income added")

    st.dataframe(income)

# ================= EXPENSE =================
elif section == "Expenses":
    st.subheader("Add Expense")

    p = st.selectbox("Person", USERS[1:])
    c = st.text_input("Category (Food, Rent, EMI, etc)")
    a = st.number_input("Amount", min_value=0.0)
    d = st.date_input("Date", date.today())

    if st.button("Save Expense"):
        expenses.loc[len(expenses)] = [d, p, c, a]
        expenses.to_csv(FILES["expenses"], index=False)
        st.success("Expense added")

    st.dataframe(expenses)

# ================= INVESTMENTS =================
elif section == "Investments":
    st.subheader("Add Investment")

    p = st.selectbox("Person", USERS[1:])
    i = st.text_input("Investment Type (MF, ETF, FD, RD, PPF, Insurance, etc)")
    a = st.number_input("Amount", min_value=0.0)
    d = st.date_input("Date", date.today())

    if st.button("Save Investment"):
        investments.loc[len(investments)] = [d, p, i, a]
        investments.to_csv(FILES["investments"], index=False)
        st.success("Investment added")

    st.dataframe(investments)

# ================= LOANS =================
elif section == "Loans":
    st.subheader("Loans Tracking")

    p = st.selectbox("Person", USERS[1:])
    t = st.selectbox("Loan Type", ["Lent", "Borrowed"])
    a = st.number_input("Amount", min_value=0.0)
    s = st.selectbox("Status", ["Open", "Closed"])
    d = st.date_input("Date", date.today())

    if st.button("Save Loan"):
        loans.loc[len(loans)] = [d, p, t, a, s]
        loans.to_csv(FILES["loans"], index=False)
        st.success("Loan entry saved")

    st.dataframe(loans)

# ================= CALCULATORS =================
elif section == "Calculators":
    st.subheader("Compound Interest Calculator")

    p = st.number_input("Principal", min_value=0.0)
    r = st.number_input("Annual Rate (%)", min_value=0.0)
    t = st.number_input("Years", min_value=0.0)

    if st.button("Calculate"):
        fv = p * ((1 + r / 100) ** t)
        st.success(f"Future Value: ₹ {fv:,.2f}")
