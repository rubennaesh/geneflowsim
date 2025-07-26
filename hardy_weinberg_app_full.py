import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random

# Page setup
st.set_page_config(page_title="GeneFlowSim", layout="wide", initial_sidebar_state="expanded")
st.title("🧬 GeneFlowSim: Hardy-Weinberg Calculator & Simulator")

# Session state for free trials
if 'tries' not in st.session_state:
    st.session_state.tries = 3

# ----------------------- Utility Functions -----------------------
def calculate_allele_frequency(aa_count, total):
    q2 = aa_count / total
    q = np.sqrt(q2)
    p = 1 - q
    return p, q

def calculate_genotype_frequencies(p, q):
    p2 = p**2
    two_pq = 2 * p * q
    q2 = q**2
    return p2, two_pq, q2

def calculate_carrier_count(two_pq, total):
    return two_pq * total

def simulate_selection(p, q, fitness, generations=10):
    history = []
    for gen in range(generations):
        p2, two_pq, q2 = calculate_genotype_frequencies(p, q)
        w_bar = p2*fitness['AA'] + two_pq*fitness['Aa'] + q2*fitness['aa']
        p2_adj = p2*fitness['AA'] / w_bar
        two_pq_adj = two_pq*fitness['Aa'] / w_bar
        q2_adj = q2*fitness['aa'] / w_bar
        p = p2_adj + 0.5*two_pq_adj
        q = 1 - p
        history.append((gen, p2_adj, two_pq_adj, q2_adj))
    return history

def simulate_mutation(p, q, mu, generations=10):
    history = []
    for gen in range(generations):
        p = p*(1-mu) + q*mu
        q = 1 - p
        history.append((gen, p, q))
    return history

def simulate_migration(p, q, p_mig, q_mig, m, generations=10):
    history = []
    for gen in range(generations):
        p = (1-m)*p + m*p_mig
        q = 1 - p
        history.append((gen, p, q))
    return history

def simulate_drift(p, q, N, generations=10):
    history = []
    for gen in range(generations):
        alleles = ['A']*int(2*N*p) + ['a']*int(2*N*q)
        sample = random.choices(alleles, k=2*N)
        p = sample.count('A')/(2*N)
        q = 1 - p
        history.append((gen, p, q))
    return history

# Plotting functions
def plot_genotype_frequencies(history):
    gens = [h[0] for h in history]
    AA = [h[1] for h in history]
    Aa = [h[2] for h in history]
    aa = [h[3] for h in history]
    fig, ax = plt.subplots()
    ax.plot(gens, AA, marker='o', label='AA')
    ax.plot(gens, Aa, marker='s', label='Aa')
    ax.plot(gens, aa, marker='^', label='aa')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Frequency')
    ax.set_title('Genotype Frequencies Over Time')
    ax.legend()
    st.pyplot(fig)

def plot_allele_history(history):
    gens = [h[0] for h in history]
    p_vals = [h[1] for h in history]
    q_vals = [h[2] for h in history]
    fig, ax = plt.subplots()
    ax.plot(gens, p_vals, label='p (A)')
    ax.plot(gens, q_vals, label='q (a)')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Allele Frequency')
    ax.set_title('Allele Frequencies Over Time')
    ax.legend()
    st.pyplot(fig)

# Sidebar: Trials & Premium
st.sidebar.header('🔒 Access & Trials')
if st.session_state.tries > 0:
    st.sidebar.info(f'Free simulations left: {st.session_state.tries}')
else:
    st.sidebar.success('Unlimited access unlocked!')
    st.sidebar.image('https://via.placeholder.com/150.png?text=Premium+User')

# Main app tabs
tabs = st.tabs([
    "🧮 Frequency Calculator",
    "🧠 Equilibrium Checker",
    "⚡ Disturbance Simulator"
])

# Tab: Frequency Calculator
with tabs[0]:
    st.header("🧮 Allele & Genotype Frequency Calculator")
    mode = st.radio("Input method:", ["Count Data", "Allele Freq."])
    if mode == "Count Data":
        total = st.number_input("Total individuals:", value=1000, min_value=1)
        aa = st.number_input("Recessive count (aa):", value=100, min_value=0, max_value=total)
        p, q = calculate_allele_frequency(aa, total)
        st.markdown(f"- q² = {aa/total:.3f}
- q = {q:.3f}
- p = {p:.3f}")
    else:
        p = st.slider("p (dominant)", 0.01, 0.99, 0.6)
        q = 1 - p
        st.markdown(f"- q = {q:.3f}")
    p2, two_pq, q2 = calculate_genotype_frequencies(p, q)
    st.subheader("Genotype Frequencies")
    st.write(f"AA (p²): {p2:.3f}")
    st.write(f"Aa (2pq): {two_pq:.3f}")
    st.write(f"aa (q²): {q2:.3f}")
    if st.checkbox("Carrier count?"):
        total2 = st.number_input("Total individuals for carriers:", value=1000, min_value=1)
        carriers = calculate_carrier_count(two_pq, total2)
        st.write(f"Carriers (Aa): {int(carriers)}")

# Tab: Equilibrium Checker
with tabs[1]:
    st.header("🧠 Hardy-Weinberg Equilibrium Checker")
    obs_AA = st.number_input("Observed AA:", min_value=0)
    obs_Aa = st.number_input("Observed Aa:", min_value=0)
    obs_aa = st.number_input("Observed aa:", min_value=0)
    total_obs = obs_AA + obs_Aa + obs_aa
    if total_obs > 0:
        p_est, q_est = calculate_allele_frequency(obs_aa, total_obs)
        p2_e, two_pq_e, q2_e = calculate_genotype_frequencies(p_est, q_est)
        st.markdown(f"- p = {p_est:.3f}
- q = {q_est:.3f}")
        st.markdown(f"Expected AA: {p2_e*total_obs:.1f} vs Observed: {obs_AA}")
        st.markdown(f"Expected Aa: {two_pq_e*total_obs:.1f} vs Observed: {obs_Aa}")
        st.markdown(f"Expected aa: {q2_e*total_obs:.1f} vs Observed: {obs_aa}")
        if st.button("Check Equilibrium"):
            st.success("Observed ≈ expected means equilibrium.")

# Tab: Disturbance Simulator
with tabs[2]:
    st.header("⚡ Disturbance Simulator")
    sim_p = st.slider("Start p", 0.01, 0.99, 0.6)
    sim_q = 1 - sim_p
    gens = st.slider("Generations", 1, 50, 10)
    disturbance = st.selectbox("Disturbance Type", ["None", "Natural Selection", "Mutation", "Migration", "Genetic Drift"])

    if disturbance == "Natural Selection":
        st.subheader("Set Fitness Values")
        fitness = {g: st.slider(f"Fitness {g}", 0.0, 1.0, 1.0 if g!='aa' else 0.5) for g in ['AA','Aa','aa']}
        if st.button("Run Sim"):
            st.session_state.tries = max(0, st.session_state.tries-1)
            history = simulate_selection(sim_p, sim_q, fitness, gens)
            plot_genotype_frequencies(history)

    elif disturbance == "Mutation":
        mu = st.slider("Mutation rate (µ)", 0.0, 0.1, 0.01)
        if st.button("Run Sim"):
            st.session_state.tries = max(0, st.session_state.tries-1)
            history = simulate_mutation(sim_p, sim_q, mu, gens)
            plot_allele_history(history)

    elif disturbance == "Migration":
        st.subheader("Migration Parameters")
        p_mig = st.slider("Migrant p", 0.01, 0.99, 0.3)
        m = st.slider("Migration rate (m)", 0.0, 1.0, 0.1)
        if st.button("Run Sim"):
            st.session_state.tries = max(0, st.session_state.tries-1)
            history = simulate_migration(sim_p, sim_q, p_mig, 1-p_mig, m, gens)
            plot_allele_history(history)

    elif disturbance == "Genetic Drift":
        N = st.number_input("Population size (N)", min_value=10, value=100)
        if st.button("Run Sim"):
            st.session_state.tries = max(0, st.session_state.tries-1)
            history = simulate_drift(sim_p, sim_q, N, gens)
            plot_allele_history(history)

    else:
        st.info("Select a disturbance and click Run Sim to see effects.")

# Footer for payment QR when out of free tries
if st.session_state.tries == 0:
    st.sidebar.image('https://via.placeholder.com/150.png?text=Scan+to+Pay+RM3')
    st.sidebar.markdown("**Upgrade to Premium for unlimited simulations!**")
