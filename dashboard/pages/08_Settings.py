import streamlit as st

from components.header import render_header
from components.sidebar import render_sidebar
from components.theme import configure_page
from components.floating_ai import floating_ai

from backend.config import config


# -----------------------------------
# Page Configuration
# -----------------------------------

configure_page()

render_sidebar()

render_header()



# -----------------------------------
# Developer Mode
# -----------------------------------

developer_mode = getattr(
    config,
    "DEVELOPER_MODE",
    False
)



# -----------------------------------
# Page Title
# -----------------------------------

st.title("⚙️ System Settings")



# -----------------------------------
# Electricity Settings
# -----------------------------------

st.subheader("⚡ Electricity Tariff Rate")


rate_input = st.number_input(

    "Rate per kWh (₹)",

    min_value=1.0,

    max_value=50.0,

    value=float(config.ELECTRICITY_RATE),

    step=0.1
)



# -----------------------------------
# Sustainability Settings
# -----------------------------------

st.subheader("🌱 CO₂ Emissions Factor")


co2_input = st.number_input(

    "kg CO₂ emissions per kWh",

    min_value=0.01,

    max_value=5.0,

    value=float(config.CO2_PER_KWH),

    step=0.01
)



st.divider()



# -----------------------------------
# AI Configuration
# Developer Only
# -----------------------------------

if developer_mode:


    st.subheader(
        "🤖 AI / LLM Configuration"
    )


    st.caption(
        "Developer settings only"
    )


    api_key_input = st.text_input(

        "Anthropic API Key",

        type="password",

        value=config.ANTHROPIC_API_KEY or "",

        help=
        "Used by AI Assistant and Insight Agent"
    )


    insight_model_input = st.text_input(

        "Insight Model",

        value=
        config.INSIGHT_MODEL
        or
        "claude-sonnet-4-6"

    )


else:


    # Keep existing values internally

    api_key_input = config.ANTHROPIC_API_KEY

    insight_model_input = config.INSIGHT_MODEL



# -----------------------------------
# Save .env Function
# -----------------------------------

def save_env_variables(variables: dict):

    env_path = config.BASE_DIR / ".env"


    lines = []


    if env_path.exists():

        try:

            with open(
                env_path,
                "r",
                encoding="utf-8"
            ) as file:

                lines = file.readlines()


        except Exception:

            pass



    updated_keys = set()

    new_lines = []



    for line in lines:


        stripped = line.strip()


        if (

            stripped

            and not stripped.startswith("#")

            and "=" in stripped

        ):


            key, value = stripped.split(
                "=",
                1
            )


            key = key.strip()



            if key in variables:


                new_lines.append(
                    f"{key}={variables[key]}\n"
                )


                updated_keys.add(key)

                continue



        new_lines.append(line)




    for key, value in variables.items():


        if key not in updated_keys:


            new_lines.append(
                f"{key}={value}\n"
            )



    try:


        with open(
            env_path,
            "w",
            encoding="utf-8"
        ) as file:


            file.writelines(new_lines)



    except Exception as e:


        st.error(
            f"❌ Failed saving configuration: {e}"
        )



# -----------------------------------
# Save Button
# -----------------------------------

if st.button(
    "💾 Save Configuration Settings",
    width="stretch"
):


    config.ELECTRICITY_RATE = rate_input

    config.CO2_PER_KWH = co2_input


    if developer_mode:


        config.ANTHROPIC_API_KEY = api_key_input

        config.INSIGHT_MODEL = insight_model_input



    save_env_variables({

        "ELECTRICITY_RATE":
        str(rate_input),


        "CO2_PER_KWH":
        str(co2_input),


        "ANTHROPIC_API_KEY":
        api_key_input,


        "INSIGHT_MODEL":
        insight_model_input

    })



    st.success(
        "✅ Configuration saved successfully."
    )



# -----------------------------------
# Floating AI Button
# -----------------------------------

floating_ai()