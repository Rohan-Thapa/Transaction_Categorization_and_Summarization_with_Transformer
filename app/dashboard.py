# The sample dashboard as for the test and for checking whether the model is working or not
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from inference import TransactionClassifier
from config import config

# Adding the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initializing the classifier
classifier = TransactionClassifier()


def main():
    st.set_page_config(
        page_title="Financial Intelligence Dashboard",
        page_icon="💰",
        layout="wide"
    )

    # Custom CSS for the dashboard
    st.markdown("""
    <style>
        .header {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .metric-box {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        }
        .stProgress > div > div > div > div {
            background-color: #2575fc;
        }
    </style>
    """, unsafe_allow_html=True)

    # Header content for the dashboard
    st.markdown("""
    <div class="header">
        <h1>💰 Financial Intelligence Dashboard</h1>
        <p>AI-powered Transaction Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = pd.DataFrame(columns=["Transaction", "Category", "Amount", "Confidence"])

    # Input Section for the data input
    with st.expander("💳 Input Transactions", expanded=True):
        input_method = st.radio("Input method:", ["Single Transaction", "Batch Input"])
        transactions = []

        if input_method == "Single Transaction":
            tx = st.text_input("Transaction:", "Paid NPR 350 for NTC mobile topup")
            transactions = [tx]
        else:
            txs = st.text_area("Transactions (one per line)",
                               "Paid NPR 350 for NTC mobile topup\nSent Rs 2000 to Sita Bank for tuition")
            transactions = [tx.strip() for tx in txs.split("\n") if tx.strip()]

        if st.button("Analyze Transactions", type="primary") and transactions:
            with st.spinner("Processing..."):
                results = classifier.categorize(transactions)

                # Converting to the DataFrame
                new_data = []
                for r in results:
                    new_data.append({
                        "Transaction": r["transaction"],
                        "Category": r["category"],
                        "Amount": r["amount"],
                        "Confidence": f"{r['confidence']:.1%}"
                    })

                new_df = pd.DataFrame(new_data)
                st.session_state.results = pd.concat([st.session_state.results, new_df])
                st.success(f"✅ Processed {len(transactions)} transactions")

    # Results Display after prediction
    if not st.session_state.results.empty:
        st.subheader("📊 Analysis Results")

        # Data Table
        st.dataframe(st.session_state.results, use_container_width=True)

        # Visualizations of the data
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Category Distribution")
            fig1 = px.pie(
                st.session_state.results,
                names='Category',
                color='Category',
                color_discrete_map=config.CATEGORY_COLORS
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Spending by Category")
            agg_df = st.session_state.results.groupby('Category')['Amount'].sum().reset_index()
            fig2 = px.bar(
                agg_df,
                x='Category',
                y='Amount',
                color='Category',
                color_discrete_map=config.CATEGORY_COLORS
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Budget Monitoring as for the test, budgeting was also added later it will be removed during the push of the code
        st.subheader("💰 Budget Monitoring")
        budgets = {
            "Food": st.number_input("Food Budget", value=10000, step=500),
            "Shopping": st.number_input("Shopping Budget", value=8000, step=500),
            "Entertainment": st.number_input("Entertainment Budget", value=5000, step=500),
            "Transportation": st.number_input("Transportation Budget", value=7000, step=500)
        }

        spending = st.session_state.results.groupby("Category")["Amount"].sum()

        for category, budget in budgets.items():
            spent = spending.get(category, 0)
            if budget > 0:
                progress = min(100, (spent / budget) * 100)
            else:
                progress = 0

            st.markdown(f"**{category}**")
            col1, col2 = st.columns([3, 1])
            col1.progress(progress / 100)
            col2.metric("", f"₹{spent} / ₹{budget}")

            if spent > budget * 0.9 and spent <= budget:
                st.warning(f"⚠️ Approaching budget limit for {category}")
            elif spent > budget:
                st.error(f"🚨 Budget exceeded for {category} by ₹{spent - budget:.2f}")


if __name__ == "__main__":
    main()
# The sample dashboard for the project.