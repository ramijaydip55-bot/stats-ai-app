import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import google.generativeai as genai

# પેજ સેટિંગ્સ
st.set_page_config(page_title="AI Statistics & Data Analyzer", layout="wide", page_icon="📊")

st.title("📊 AI Automated Statistics & Data Analyzer")
st.markdown("તમારો ડેટા (CSV/Excel) અપલોડ કરો અને AI ની મદદથી તુરંત એક્યુરેટ વિશ્લેષણ તથા ગ્રાફ મેળવો.")

# સાઇડબાર
st.sidebar.header("⚙️ સેટિંગ્સ અને અપલોડ")
api_key = st.sidebar.text_input("Gemini API Key દાખલ કરો:", type="password")

uploaded_file = st.sidebar.file_uploader("CSV અથવા Excel ફાઇલ અપલોડ કરો", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("૧. 📋 ડેટા પ્રિવ્યૂ અને સમરી")
        tab1, tab2, tab3 = st.tabs(["Data Preview", "Descriptive Statistics", "Data Types & Missing Values"])
        
        with tab1:
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"કુલ હરોળ (Rows): {df.shape[0]} | કુલ કોલમ (Columns): {df.shape[1]}")

        with tab2:
            st.write("**આપોઆપ ગણતરી (Mean, Std, Min, Max, Quartiles):**")
            st.dataframe(df.describe(), use_container_width=True)

        with tab3:
            missing_info = pd.DataFrame({
                "Data Type": df.dtypes,
                "Missing Values": df.isnull().sum(),
                "Missing (%)": (df.isnull().sum() / len(df)) * 100
            })
            st.dataframe(missing_info, use_container_width=True)

        st.divider()

        st.subheader("૨. 🤖 AI સાથે ઓટોમેટિક એનાલિસિસ & વિઝ્યુઅલાઈઝેશન")

        if not api_key:
            st.warning("⚠️ કૃપા કરીને સાઇડબારમાં તમારી મફત Gemini API Key દાખલ કરો.")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.8-flash')
            user_query = st.text_input(
                "તમે ડેટામાં શું એનાલાઈઝ કરવા માંગો છો? (સાદી ભાષામાં લખો)",
                placeholder="દા.ત. Plot histogram for marks with box plot, અથવા Show correlation matrix"
            )

            if st.button("ગ્રાફ બનાવો 🚀") and user_query:
                schema_dict = {col: str(dtype) for col, dtype in df.dtypes.items()}
                prompt = f"""
                You are a senior statistical programmer.
                Dataset Columns and Data Types: {schema_dict}
                User Request: "{user_query}"
                Rules:
                1. Write ONLY valid Python code using plotly.express as px or plotly.figure_factory as ff.
                2. Assume dataframe is loaded as df.
                3. Assign final plotly figure to variable fig.
                4. Do NOT output markdown codeblocks (no ```python). Raw code only.
                """

                with st.spinner("AI ગ્રાફ તૈયાર કરી રહ્યું છે..."):
                    try:
                        ai_response = model.generate_content(prompt)
                        code = ai_response.text.replace("```python", "").replace("```", "").strip()

                        local_scope = {"df": df, "px": px, "ff": ff, "np": np, "pd": pd}
                        exec(code, {}, local_scope)

                        if "fig" in local_scope:
                            st.plotly_chart(local_scope["fig"], use_container_width=True)
                            with st.expander("AI Code"):
                                st.code(code, language="python")
                    except Exception as err:
                        st.error(f"ભૂલ આવી: {err}")
    except Exception as e:
        st.error(f"ફાઇલ વાંચવામાં ક્ષતિ: {e}")
else:
    st.info("👈 કૃપા કરીને સાઇડબારમાંથી ફાઇલ અપલોડ કરો.")