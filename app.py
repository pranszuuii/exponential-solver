import streamlit as st
import sympy as sp
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="False Position using Exponential", page_icon="🔬", layout="wide")

# CSS para sa Presko at Professional look (Mint & Navy Theme)
st.markdown("""
    <style>
    .stApp { background-color: #f4f9f9; }
    .input-card { background-color: #ffffff; padding: 25px; border-radius: 15px; border: 1px solid #e0f2f1; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
    div[data-testid="stMetricValue"] { color: #00796b; font-weight: bold; }
    .step-card { 
        background-color: white; border-radius: 10px; padding: 20px; 
        margin-bottom: 20px; border-left: 6px solid #4db6ac;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.02);
    }
    .final-verdict {
        background-color: #e0f2f1;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #4db6ac;
        color: #004d40;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AUTO-BRACKETING LOGIC ---
def find_valid_bracket(f, a, b):
    search_range = 2.0
    for _ in range(50): 
        if f(a) * f(b) < 0:
            return a, b, True
        a -= search_range
        b += search_range
    return a, b, False

# --- HEADER ---
st.title("🔬 False Position - Exponential Solver")
st.markdown("##### Developed by Andy Lasala and Francis Mangalindan")
st.write("---")

# --- INPUT TABLE (Main Body) ---
with st.container():
    st.markdown("### 📋 System Input Table")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1: func_input = st.text_input("Function f(x)", "exp(x) - 20")
    with c2: a_in = st.number_input("Lower Bound (a)", value=2.0, format="%.4f")
    with c3: b_in = st.number_input("Upper Bound (b)", value=3.0, format="%.4f")
    with c4: tol = st.number_input("Tolerance (ε)", value=0.0001, format="%.6f")

    run_btn = st.button("🚀 EXECUTE FULL ANALYSIS", use_container_width=True)

if run_btn:
    try:
        # Math Setup
        x_sym = sp.symbols('x')
        expr = sp.sympify(func_input)
        f_num = sp.lambdify(x_sym, expr, 'numpy')

        # Check and Auto-Bracket
        a, b = a_in, b_in
        is_valid = True
        if f_num(a) * f_num(b) >= 0:
            st.warning("⚠️ **No Sign Change:** System is searching for a valid interval...")
            a, b, found = find_valid_bracket(f_num, a, b)
            if not found:
                st.error("❌ **Search Failed:** Could not find a root automatically.")
                is_valid = False
            else:
                st.success(f"✅ **Interval Adjusted:** [{a:.2f}, {b:.2f}]")

        if is_valid:
            data, detailed_steps = [], []
            z_old = 0
            
            for i in range(1, 21): # Up to 20 iterations
                fa, fb = f_num(a), f_num(b)
                z = (a * fb - b * fa) / (fb - fa)
                fz = f_num(z)
                err = abs((z - z_old)/z)*100 if i > 1 else 100
                
                data.append({"Iter": i, "a": a, "b": b, "f(a)": fa, "f(b)": fb, "z": z, "f(z)": fz, "Error%": err})
                detailed_steps.append({"iter": i, "a": a, "b": b, "fa": fa, "fb": fb, "z": z, "fz": fz})

                if abs(fz) < tol: break
                if f_num(a) * fz < 0: b = z
                else: a = z
                z_old = z

            df = pd.DataFrame(data)

            # --- DISPLAY TABS ---
            tab1, tab2, tab3 = st.tabs(["📊 Analytics & Table", "📝 Step-by-Step Long Hand", "📥 Export"])

            with tab1:
                st.markdown("#### 📑 Iteration Summary Table")
                st.dataframe(df.style.format("{:.6f}"), use_container_width=True)
                
                # Plotly Graph
                x_vals = np.linspace(a_in - 1, b_in + 1, 200)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_vals, y=f_num(x_vals), name="f(x)", line=dict(color='#00796b', width=3)))
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                fig.add_trace(go.Scatter(x=[z], y=[0], mode='markers', marker=dict(size=12, color='red'), name="Root"))
                fig.update_layout(template="plotly_white", title="Convergence Graph")
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.markdown("### 🖋️ Detailed Mathematical Solution")
                for s in detailed_steps:
                    with st.container():
                        st.markdown(f'<div class="step-card"><h4>Iteration {s["iter"]}</h4>', unsafe_allow_html=True)
                        st.write(f"**Step 1:** Given $a = {s['a']:.6f}, f(a) = {s['fa']:.6f}$ and $b = {s['b']:.6f}, f(b) = {s['fb']:.6f}$")
                        st.latex(r"z = \frac{a \cdot f(b) - b \cdot f(a)}{f(b) - f(a)}")
                        st.latex(f"z = \\frac{{({s['a']:.4f})({s['fb']:.4f}) - ({s['b']:.4f})({s['fa']:.4f})}}{{{s['fb']:.4f} - ({s['fa']:.4f})}} = {s['z']:.6f}")
                        st.write(f"**Step 2:** $f(z) = {s['fz']:.8f}$")
                        st.markdown(f"**Result:** Replace {'b' if f_num(s['a'])*s['fz'] < 0 else 'a'} with z.</div>", unsafe_allow_html=True)

            with tab3:
                st.download_button("📂 Download CSV Report", df.to_csv(index=False).encode('utf-8'), "Report.csv", "text/csv")

            # --- THE FINAL ANSWER (Dito makikita ang sagot) ---
            st.write("---")
            st.markdown(f"""
                <div class="final-verdict">
                    <h2 style='text-align: center; color: #004d40;'>🎯 Final Answer</h2>
                    <p style='text-align: center; font-size: 24px;'>
                        The calculated root for the function <b>{func_input}</b> is approximately:<br>
                        <span style='font-size: 40px; font-weight: bold;'>z ≈ {z:.6f}</span>
                    </p>
                    <p style='text-align: center;'>Converged in {len(df)} iterations with a residual error of {fz:.2e}.</p>
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ **Math Error:** Please use standard syntax. Example: exp(x)-20. Error: {e}")
