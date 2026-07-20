import streamlit as st
from components.header import render_header
from components.sidebar import render_sidebar
from components.theme import configure_page
from backend.config import config

configure_page()
render_sidebar()
render_header()

st.title("⚙️ System Settings")

st.subheader("⚡ Electricity tariff rate")
rate_input = st.number_input(
    "Rate per kWh (₹)",
    min_value=1.0,
    max_value=50.0,
    value=config.ELECTRICITY_RATE,
    step=0.1
)

st.subheader("🌱 CO₂ emissions factor")
co2_input = st.number_input(
    "kg CO₂ emissions per kWh",
    min_value=0.01,
    max_value=5.0,
    value=config.CO2_PER_KWH,
    step=0.01
)

st.subheader("🤖 AI / LLM Configuration")
api_key_input = st.text_input(
    "Anthropic API Key",
    type="password",
    value=config.ANTHROPIC_API_KEY or "",
    help="Enter your Anthropic API Key to enable Claude-powered reasoning in the Insight Agent and AI Assistant."
)

insight_model_input = st.text_input(
    "Insight Model",
    value=config.INSIGHT_MODEL or "claude-sonnet-4-6",
    help="The Anthropic model to use (default: claude-sonnet-4-6)."
)

def save_env_variables(variables: dict):
    env_path = config.BASE_DIR / ".env"
    lines = []
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            pass
    
    updated_keys = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            try:
                key, val = stripped.split("=", 1)
                key = key.strip()
                if key in variables:
                    new_lines.append(f"{key}={variables[key]}\n")
                    updated_keys.add(key)
                    continue
            except ValueError:
                pass
        new_lines.append(line)
        
    for key, val in variables.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={val}\n")
            
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        st.error(f"Failed to write to .env file: {e}")

if st.button("Save Configuration Settings"):
    config.ELECTRICITY_RATE = rate_input
    config.CO2_PER_KWH = co2_input
    config.ANTHROPIC_API_KEY = api_key_input
    config.INSIGHT_MODEL = insight_model_input
    
    save_env_variables({
        "ELECTRICITY_RATE": str(rate_input),
        "CO2_PER_KWH": str(co2_input),
        "ANTHROPIC_API_KEY": api_key_input,
        "INSIGHT_MODEL": insight_model_input
    })
    st.success("✅ Configuration saved and persisted to .env successfully!")
