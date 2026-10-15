import os
import requests
import streamlit as st
from PIL import Image

Page configuration

st.set_page_config(
page_title="AI Ayurvedic Herbal Knowledge System",
page_icon="🌿",
layout="wide",
initial_sidebar_state="expanded"
)

API configuration

API_URL = st.secrets.get(
"API_URL",
os.getenv("API_URL", "")
).rstrip("/")

Custom styling

st.markdown("""

<style>
    .main-title {
        font-size: 32px;
        font-weight: 700;
        text-align: center;
        color: #287447;
    }
    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #666666;
    }
    .result-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #d8e8dc;
        margin-top: 12px;
    }
    .disclaimer {
        font-size: 13px;
        color: #777777;
    }
</style>""", unsafe_allow_html=True)

Header

st.markdown(
'<div class="main-title">🌿 AI-Based Ayurvedic Herbal Knowledge System</div>',
unsafe_allow_html=True
)
st.markdown(
'<div class="subtitle">Medicinal Plant Identification and Traditional Herbal Knowledge</div>',
unsafe_allow_html=True
)

st.divider()

Sidebar

with st.sidebar:
st.header("About the Project")
st.write(
"This academic project uses an AI image-classification model "
"to predict medicinal plant classes and display available herbal information."
)

st.subheader("How to use")
st.write("1. Upload a plant image.")
st.write("2. Click Predict Plant.")
st.write("3. Review the prediction and available information.")

st.divider()
st.caption("AI prediction is not expert-confirmed identification.")

Main layout

left_column, right_column = st.columns([1, 1], gap="large")

with left_column:
st.subheader("📷 Upload Plant Image")

uploaded_file = st.file_uploader(
    "Choose an image of a plant",
    type=["jpg", "jpeg", "png"],
    help="Supported formats: JPG, JPEG and PNG"
)

if uploaded_file:
    try:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(
            image,
            caption="Uploaded Plant Image",
            use_container_width=True
        )
    except Exception:
        st.error("This image could not be opened. Please upload another image.")
        st.stop()

predict_button = st.button(
    "🌱 Predict Plant",
    type="primary",
    use_container_width=True,
    disabled=uploaded_file is None
)

with right_column:
st.subheader("🔎 Prediction Result")

if predict_button and uploaded_file is not None:
    if not API_URL:
        st.error(
            "Prediction API URL is not configured. "
            "Set API_URL in Streamlit app secrets after deploying your API."
        )
    else:
        try:
            with st.spinner("AI is analysing the plant image..."):
                uploaded_file.seek(0)

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

            if response.status_code == 200:
                result = response.json()
                plant_name = result.get("predicted_plant", "Unknown")
                confidence = result.get("confidence", 0)
                information = result.get("plant_information", {})

                st.success("Prediction completed")

                st.markdown("### 🌿 " + str(plant_name))
                st.metric(
                    label="Model Confidence",
                    value=f"{confidence}%"
                )

                if isinstance(confidence, (int, float)) and confidence < 70:
                    st.warning(
                        "Confidence is relatively low. The prediction "
                        "may be incorrect; verify the plant with an expert."
                    )

                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("### Herbal Information")

                st.write(
                    "**Common Name:**",
                    information.get("common_name", "Not available")
                )
                st.write(
                    "**Scientific Name:**",
                    information.get("scientific_name", "Not available")
                )

                st.write("**Traditional Uses:**")
                uses = information.get("traditional_uses", [])

                if isinstance(uses, list) and uses:
                    for use in uses:
                        st.write(f"- {use}")
                elif isinstance(uses, str) and uses:
                    st.write(uses)
                else:
                    st.write("No traditional-use information available.")

                optional_fields = {
                    "Properties": "properties",
                    "Constituents": "constituents",
                    "Formulations": "formulations",
                    "Related Herbs": "related_herbs",
                    "Safety Notes": "safety_notes",
                    "Evidence References": "evidence_references"
                }

                for label, key in optional_fields.items():
                    value = information.get(key)
                    if value:
                        st.write(f"**{label}:**", value)

                st.markdown("</div>", unsafe_allow_html=True)

                note = information.get("note")
                if note:
                    st.info(note)

                st.warning(
                    result.get(
                        "disclaimer",
                        "AI prediction is not confirmed plant identification "
                        "or medical advice."
                    )
                )

            else:
                st.error(
                    f"Prediction API returned HTTP {response.status_code}."
                )
                st.caption("Check whether the API is running and reachable.")

        except requests.exceptions.Timeout:
            st.error("The prediction request timed out. Please try again.")
        except requests.exceptions.RequestException:
            st.error(
                "Could not connect to the prediction API. "
                "Check the API URL and confirm that the API is running."
            )
        except (ValueError, KeyError):
            st.error("The API returned an unexpected response.")
else:
    st.info("Upload a plant image and click Predict Plant to see the result.")

st.divider()

Footer

st.markdown("### ⚠️ Important Disclaimer")
st.markdown(
'<div class="disclaimer">'
"This project is for educational and informational purposes only. "
"AI predictions can be incorrect and do not confirm plant identity. "
"Traditional uses are not proof of clinical effectiveness. "
"Do not use a plant as treatment based only on this application. "
"Consult a qualified healthcare professional before medicinal use."
"</div>",
unsafe_allow_html=True
)

st.caption("AI-Based Ayurvedic Herbal Knowledge and Recommendation System")
