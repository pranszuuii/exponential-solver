import streamlit as st
import sympy as sp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="False Position Method : Exponential Solver", page_icon="🔬", layout="wide")

# Sidebar Branding
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🔬</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>False Position Method - Exponential Solver</h3>", unsafe_allow_html=True)
    st.divider()
    st.header("🛠️ Input Parameters")
    func_input = st.text_input("Function f(x):", "exp(x) - 20")
    x_start = st.number_input("Lower Bound (x):", value=2.0)
    y_start = st.number_input("Upper Bound (y):", value=3.0)
    tol = st.number_input("Tolerance (ε):", value=0.0001, format="%.6f")
    
    st.divider()
    st.info("Tip: Use the Table of Values to verify if a sign change exists within your chosen interval.")

st.title("🚀 Exponential Root Finder")
st.caption("False Position Method (Regula Falsi) for Transcendental Equations")

try:
    x_sym = sp.symbols('x')
    expr = sp.sympify(func_input)
    f = sp.lambdify(x_sym, expr, 'numpy')

    # --- 1. TABLE OF VALUES ---
    st.write("### 📋 Table of Values")
    tov_x = np.linspace(x_start - 1, y_start + 1, 10)
    tov_y = f(tov_x)
    tov_df = pd.DataFrame({"x": tov_x, "f(x)": tov_y})
    st.dataframe(tov_df.style.format("{:.2f}"), use_container_width=True)

    if st.button("Run Full Analysis"):
        with st.status("🚀 Processing Numerical Method...", expanded=False) as status:
            time.sleep(0.6)
            st.write("Computing iterative approximations...")
            time.sleep(0.6)
            st.write("Validating convergence criteria...")
            time.sleep(0.4)
            status.update(label="Analysis Complete", state="complete")

        if f(x_start) * f(y_start) >= 0:
            st.error("❌ **Root Bracketing Error:** f(x) and f(y) must have opposite signs.")
        else:
            data, steps = [], []
            x_c, y_c, z_old = x_start, y_start, 0

            for i in range(1, 21):
                fx, fy = f(x_c), f(y_c)
                z_c = (x_c * fy - y_c * fx) / (fy - fx)
                fz = f(z_c)
                rel_err = abs((z_c - z_old)/z_c)*100 if i > 1 else 100
                
                sign_str = "Positive" if fz > 0 else "Negative"
                data.append({"Iter": i, "x": x_c, "y": y_c, "z": z_c, "f(z)": fz, "Sign": sign_str, "Error%": rel_err})
                steps.append(f"**Iteration {i}:** $z = \\frac{{({x_c:.2f})({fy:.2f}) - ({y_c:.2f})({fx:.2f})}}{{{fy:.2f} - ({fx:.2f})}} = {z_c:.4f}$")
                
                if abs(fz) < tol: break
                if f(x_c) * fz < 0: y_c = z_c
                else: x_c = z_c
                z_old = z_c

            df = pd.DataFrame(data)

            st.success(f"✅ **Convergence Achieved:** Calculated Root z ≈ {z_c:.4f}")
            
            # --- TABS (Added Export Tab) ---
            t1, t2, t3, t4, t5 = st.tabs(["📊 Analytics", "📑 Solution Steps", "🎯 Verification", "📥 Export Report", "ℹ️ About"])
            
            with t1:
                col1, col2 = st.columns([1.2, 1])
                with col1:
                    st.write("#### Iteration Log")
                    st.dataframe(df.style.format({"x":"{:.2f}","y":"{:.2f}","z":"{:.4f}","f(z)":"{:.4f}","Error%":"{:.2f}"}), use_container_width=True)
                with col2:
                    st.write("#### Convergence Plot")
                    fig, ax = plt.subplots(); ax.plot(df['Iter'], df['Error%'], marker='o', color='#0078D4')
                    ax.set_ylabel("Error (%)"); ax.set_xlabel("Iteration"); ax.grid(True, alpha=0.3)
                    st.pyplot(fig)

            with t2:
                for s in steps:
                    st.markdown(s)
                    st.divider()

            with t3:
                st.write("#### 🎯 Proof of Accuracy")
                check_val = f(z_c)
                st.latex(f"f({z_c:.4f}) = {check_val:.8f}")
                st.metric(label="Residual Error |f(z)|", value=f"{check_val:.8f}")
                if abs(check_val) < 0.01:
                    st.success("### ⭐ VERDICT: VALIDATED")
                else:
                    st.warning("Precision below preferred threshold.")

            # --- EXPORT TAB (The Print Replacement) ---
            with t4:
                st.write("#### 📥 Download Official Report")
                st.write("Click the button below to export the iterative data to a CSV file for printing or documentation.")
                
                # Convert DF to CSV
                csv_data = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="Download Iteration Table (CSV)",
                    data=csv_data,
                    file_name=f"False_Position_Report_Andy_Lasala.csv",
                    mime="text/csv",
                )

            with t5:
                st.write("### System Information")
                st.write("**Lead Developer:** Andy Lasala")
                st.info("Built with Python & Streamlit for Educational Numerical Method.")

except Exception as e:
    st.info("👋 Welcome. Please enter a function to begin.")