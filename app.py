
import os
import requests
import streamlit as st
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="AI Ayurvedic Herbal Knowledge System",
    page_icon="🌿",
    layout="wide"
)

# API configuration
API_URL = st.secrets.get("API_URL", os.getenv("API_URL", "")).rstrip("/")

# Header
st.title("🌿 AI-Based Ayurvedic Herbal Knowledge System")
st.write("Upload a medicinal plant image to identify the plant.")

# Sidebar
with st.sidebar:
    st.header("About the Project")
    st.write("This academic project uses AI.")
    st.subheader("How to use")
    st.write("1. Upload a plant image.")
    st.write("2. Click Predict Plant.")
    st.write("3. Review the prediction.")

# Main layout
left_column, right_column = st.columns(2)

with left_column:
    st.subheader("📷 Upload Plant Image")
    uploaded_file = st.file_uploader(
        "Choose a plant image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(
                image,
                caption="Uploaded Plant Image",
                use_container_width=True
            )
        except Exception:
            st.error("Could not open this image.")
            st.stop()

    predict_button = st.button(
        "🌱 Predict Plant",
        type="primary",
        disabled=uploaded_file is None
    )

with right_column:
    st.subheader("🔎 Prediction Result")

    if predict_button and uploaded_file is not None:
        if not API_URL:
            st.error(
                "API URL is missing. Configure API_URL in Streamlit Secrets."
            )
        else:
            try:
                with st.spinner("Analysing plant image..."):
                    response = requests.post(
                        f"{API_URL}/predict",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type or "image/jpeg"
                            )
                        },
                        timeout=120
                    )

                if response.ok:
                    result = response.json()
                    info = result.get("plant_information", {})

                    st.success(
                        f"Predicted Plant: {result.get('predicted_plant', 'Unknown')}"
                    )
                    st.metric(
                        "Model Confidence",
                        f"{result.get('confidence', 0)}%"
                    )

                    st.subheader("🌿 Herbal Information")
                    st.write(
                        "**Common Name:**",
                        info.get("common_name", "Not available")
                    )
                    st.write(
                        "**Scientific Name:**",
                        info.get("scientific_name", "Not available")
                    )

                    st.write("**Traditional Uses:**")
                    uses = info.get("traditional_uses", [])

                    if isinstance(uses, list) and uses:
                        for use in uses:
                            st.write(f"- {use}")
                    elif isinstance(uses, str) and uses:
                        st.write(uses)
                    else:
                        st.write("Information not available.")

                    for label, key in {
                        "Properties": "properties",
                        "Constituents": "constituents",
                        "Formulations": "formulations",
                        "Related Herbs": "related_herbs",
                        "Safety Notes": "safety_notes",
                        "Evidence References": "evidence_references"
                    }.items():
                        value = info.get(key)
                        if value:
                            st.write(f"**{label}:** {value}")

                    st.info(
                        info.get(
                            "note",
                            "Traditional information only; not medical advice."
                        )
                    )
                    st.warning(
                        result.get(
                            "disclaimer",
                            "AI prediction is not confirmed plant identification or medical advice."
                        )
                    )
                else:
                    st.error(f"API error: HTTP {response.status_code}")
                    st.caption(response.text[:500])

            except requests.exceptions.RequestException as error:
                st.error("Could not connect to the prediction API.")
                st.caption(str(error))
    else:
        st.info("Upload a plant image and click Predict Plant.")

st.divider()
st.subheader("⚠️ Important Disclaimer")
st.write(
    "This project is for educational purposes only. AI predictions may be "
    "incorrect and do not confirm plant identity. Traditional uses are not "
    "proof of clinical effectiveness. Consult qualified professionals before "
    "using any plant medicinally."
)
