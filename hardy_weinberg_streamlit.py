# hardy_weinberg_app.py
# A free, mobile-responsive Hardy-Weinberg simulation app using Streamlit
# Users get 3 free calculations, unlimited with manual RM3 scan-and-pay unlock.

import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image

# Initialize try counter
if 'tries' not in st.session_state:
    st.session_state.tries = 3

# App title and branding
st.set_page_config(page_title="GeneFlowSim", layout="wide")  # Responsive by default ([discuss.streamlit.io](https://discuss.streamlit.io/t/streamlit-responsive-ui/34879?utm_source=chatgpt.com))
st.image("https://via.placeholder.com/300x80.png?text=GeneFlowSim+Logo", use_column_width=False)
st.title("GeneFlowSim: Hardy-Weinberg Simulator")

# Display description
st.markdown(
    "Interactively calculate and visualize genotype frequencies."
    " You have **3 free trials**—scan the QR below to unlock unlimited simulations for RM3."
)

# Check trial availability
if st.session_state.tries > 0:
    # Input panel in two columns
    col1, col2 = st.columns(2)
    with col1:
        choice = st.radio("Input mode:", ("Count data", "Allele frequencies"))
        if choice == "Count data":
            total = st.number_input("Total individuals:", min_value=1, step=1, value=100)
            aa = st.number_input("Recessive count (aa):", min_value=0, max_value=total, step=1)
            q2 = aa / total
            q = q2**0.5
            p = 1 - q
        else:
            p = st.slider("Dominant allele frequency (p):", 0.01, 0.99, 0.6)
            q = 1 - p
    with col2:
        gens = st.slider("Generations to simulate:", 1, 20, 5)
        if st.button("Simulate"):
            st.session_state.tries -= 1

            # Calculate genotype frequencies
            p2 = p**2
            two_pq = 2 * p * q
            q2 = q**2

            # Display results
            st.subheader("Genotype Frequencies (Generation 0)")
            st.write(f"AA (p²): {p2:.3f}")
            st.write(f"Aa (2pq): {two_pq:.3f}")
            st.write(f"aa (q²): {q2:.3f}")

            # Plot bar chart
            fig, ax = plt.subplots()
            ax.bar(['AA', 'Aa', 'aa'], [p2, two_pq, q2])
            ax.set_xlabel('Genotype')
            ax.set_ylabel('Frequency')
            ax.set_title('Genotype Frequencies')
            st.pyplot(fig)

            st.info(f"Simulations left: {st.session_state.tries}")
    # Footer & QR for payment
    if st.session_state.tries == 0:
        st.warning("You’ve used all free trials.")
        st.markdown("**Upgrade to unlimited simulations for RM3**")
        st.image("/path/to/duitinow_qr.png", width=200)
else:
    st.warning("Unlimited trials unlocked.")
    # Repeat input panel without decrementing tries
    st.markdown("_You have unlimited access._")
    # (Repeat simulation code here or refactor into function)

# Deployment instruction:
# 1. Push this file to GitHub.
# 2. Connect repo to Streamlit Community Cloud and deploy. ([blog.streamlit.io](https://blog.streamlit.io/host-your-streamlit-app-for-free/?utm_source=chatgpt.com))
# 3. Share the generated link—works on mobile, tablets, and desktop automatically.
