
import os
import requests
import streamlit as st
from PIL import Image, UnidentifiedImageError

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="AI Ayurvedic Herbal Knowledge System",
    page_icon="🌿",
    layout="wide"
)

# =====================================================
# CONFIGURATION
# =====================================================
try:
    API_URL = st.secrets.get(
        "API_URL",
        os.getenv("API_URL", "")
    ).strip().rstrip("/")
except Exception:
    API_URL = os.getenv("API_URL", "").strip().rstrip("/")

# Illustrative threshold only; calibrate using validation data.
LOW_CONFIDENCE_THRESHOLD = 50.0

DISCLAIMER = (
    "This project is for educational purposes only. AI predictions "
    "may be incorrect and do not confirm plant identity. Traditional "
    "uses are not proof of clinical effectiveness. Do not consume or "
    "prepare a plant based on an AI prediction. Consult qualified "
    "professionals before using any plant medicinally."
)

# =====================================================
# HEADER
# =====================================================
st.title("🌿 AI-Based Ayurvedic Herbal Knowledge System")

st.write(
    "Upload an image of a medicinal plant to obtain an AI-generated "
    "prediction and educational herbal information."
)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.header("📘 About the Project")
    st.write(
        "This academic project uses artificial intelligence "
        "to predict medicinal plants from images."
    )

    st.subheader("How to use")
    st.markdown(
        """
        1. Upload a plant image.
        2. Click **Predict Plant**.
        3. Review the prediction and confidence.
        4. Check the available educational information.
        """
    )

    st.divider()
    st.caption(
        "AI predictions are not confirmed plant identifications "
        "or medical advice."
    )

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def display_field(label, value):
    """Display an available information field safely."""
    if value is not None and value != "" and value != []:
        st.markdown(f"**{label}:** {value}")
    else:
        st.markdown(f"**{label}:** Not available in the database")


def display_herbal_information(info):
    """Display herbal information returned by the API."""
    if not isinstance(info, dict):
        info = {}

    st.subheader("🌿 Herbal Information")

    display_field(
        "Common Name",
        info.get("common_name") or "Not verified"
    )
    display_field(
        "Scientific Name",
        info.get("scientific_name") or "Not verified"
    )

    st.markdown("**Traditional Uses:**")
    uses = info.get("traditional_uses", [])

    if isinstance(uses, list) and uses:
        for use in uses:
            st.markdown(f"- {use}")
    elif isinstance(uses, str) and uses.strip():
        st.write(uses)
    else:
        st.info("No traditional-use information is available.")

    fields = [
        ("Properties", "properties"),
        ("Constituents", "constituents"),
        ("Formulations", "formulations"),
        ("Related Herbs", "related_herbs"),
        ("Safety Notes", "safety_notes"),
        ("Evidence References", "evidence_references"),
    ]

    for label, key in fields:
        value = info.get(key)

        if value:
            if isinstance(value, list):
                st.markdown(f"**{label}:**")
                for item in value:
                    st.markdown(f"- {item}")
            else:
                display_field(label, value)

    note = info.get("note")
    if note:
        st.info(str(note))


def predict_plant(uploaded_file):
    """Send an image to the prediction API."""
    if not API_URL:
        st.error(
            "Prediction API URL is missing. Configure API_URL "
            "in Streamlit Secrets or as an environment variable."
        )
        return

    try:
        image_bytes = uploaded_file.getvalue()

        with st.spinner("🔍 Analysing the plant image..."):
            response = requests.post(
                f"{API_URL}/predict",
                files={
                    "file": (
                        uploaded_file.name,
                        image_bytes,
                        uploaded_file.type or "image/jpeg"
                    )
                },
                timeout=(10, 120)
            )

        if not response.ok:
            st.error(
                f"Prediction API returned HTTP "
                f"{response.status_code}."
            )
            st.caption(response.text[:500])
            return

        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            st.error("The prediction API returned invalid JSON.")
            return

        if not isinstance(result, dict):
            st.error("The prediction API returned an unexpected response.")
            return

        if result.get("error"):
            st.error(str(result["error"]))
            return

        plant_name = result.get("predicted_plant") or "Unknown"

        try:
            confidence = float(result.get("confidence", 0))
        except (TypeError, ValueError):
            st.error("The API returned an invalid confidence value.")
            return

        if (
            not confidence >= 0
            or confidence > 100
        ):
            st.error("The API returned an invalid confidence percentage.")
            return

        st.subheader("🔎 Prediction Result")

        st.markdown(f"### Predicted Plant: {plant_name}")
        st.metric(
            label="Model Confidence",
            value=f"{confidence:.2f}%"
        )

        if confidence < LOW_CONFIDENCE_THRESHOLD:
            st.warning(
                "⚠️ Low-confidence prediction. The model is uncertain "
                "about this result. Try a clear, well-lit image showing "
                "the plant's leaves and other identifying features."
            )
            st.info(
                "Do not rely on this prediction to identify, consume, "
                "or prepare a medicinal plant."
            )
        else:
            st.info(
                "This is an AI-generated prediction, not a confirmed "
                "plant identification. Confidence is not the same "
                "as accuracy."
            )

        # Display information associated with the predicted class.
        info = result.get("plant_information") or {}
        display_herbal_information(info)

        st.warning(
            result.get("disclaimer") or DISCLAIMER
        )

    except requests.exceptions.Timeout:
        st.error(
            "The prediction request timed out. Please try again later."
        )

    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the prediction API. Check the "
            "API URL and confirm that your backend is running."
        )

    except requests.exceptions.RequestException as error:
        st.error("An error occurred while requesting a prediction.")
        st.caption(str(error))

# =====================================================
# MAIN LAYOUT
# =====================================================
left_column, right_column = st.columns(2)

with left_column:
    st.subheader("📷 Upload Plant Image")

    uploaded_file = st.file_uploader(
        "Choose a plant image",
        type=["jpg", "jpeg", "png"],
        help="Upload a JPG, JPEG, or PNG image."
    )

    valid_image = False

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            image.verify()

            uploaded_file.seek(0)
            image = Image.open(uploaded_file).convert("RGB")

            st.image(
                image,
                caption="Uploaded Plant Image",
                use_container_width=True
            )
            valid_image = True

        except (UnidentifiedImageError, OSError, ValueError):
            st.error(
                "Unable to read this image. Please upload a valid "
                "JPG, JPEG, or PNG file."
            )

    predict_button = st.button(
        "🌱 Predict Plant",
        type="primary",
        disabled=not valid_image,
        use_container_width=True
    )

with right_column:
    st.subheader("🔎 Prediction Result")

    if predict_button and uploaded_file is not None and valid_image:
        predict_plant(uploaded_file)
    else:
        st.info(
            "Upload a valid plant image and click Predict Plant "
            "to view the prediction."
        )

# =====================================================
# DISCLAIMER
# =====================================================
st.divider()
st.subheader("⚠️ Important Disclaimer")
st.write(DISCLAIMER)

st.caption(
    "Scientific names and herbal information should be verified "
    "against reliable botanical and scientific references."
)
