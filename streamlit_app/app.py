import streamlit as st
import httpx

# Point to your local orchestrator
ORCHESTRATOR_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="Stock Insights", layout="centered")

st.title("📈Stock Insight Assistant")

query = st.text_input("Ask a question about a company:", placeholder="e.g. Tell me about Apple stocks")

if st.button("Get Insight"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Analyzing your request..."):
            try:
                response = httpx.post(ORCHESTRATOR_URL, json={"query": query}, timeout=90.0)
                if response.status_code == 200:
                    result = response.text.strip()
                    st.success("✅ Here's what I found:")
                    st.markdown(result["result"])
                else:
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"❌ Failed to connect to orchestrator: {e}")
