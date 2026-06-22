import pandas as pd
import numpy as np
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
import pickle
import base64

st.set_page_config(page_title="Boston House Price Prediction", layout="wide")

st.title("🏠 Boston House Price Prediction App")

# Load Dataset
data_url = "http://lib.stat.cmu.edu/datasets/boston"
raw_df = pd.read_csv(data_url, sep=r"\s+", skiprows=22, header=None)

data = np.hstack([
    raw_df.values[::2, :],
    raw_df.values[1::2, :2]
])

target = raw_df.values[1::2, 2]

columns = [
    "CRIM", "ZN", "INDUS", "CHAS", "NOX",
    "RM", "AGE", "DIS", "RAD", "TAX",
    "PTRATIO", "B", "LSTAT"
]

df = pd.DataFrame(data, columns=columns)
df["MEDV"] = target

# Features & Target
X = df.drop("MEDV", axis=1)
y = df["MEDV"]

# Split Data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Models
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(random_state=42),
    "XGBoost": XGBRegressor(
        random_state=42,
        objective="reg:squarederror"
    )
}

# Train Models
for model in models.values():
    model.fit(X_train, y_train)

# Dataset Overview
st.subheader("📊 Dataset Overview")

col1, col2 = st.columns(2)

with col1:
    st.metric("Rows", df.shape[0])

with col2:
    st.metric("Columns", df.shape[1])

st.dataframe(df.head())

# House Price Distribution
st.subheader("🏠 House Price Distribution")
st.bar_chart(df["MEDV"])

# Correlation Matrix
st.subheader("🔥 Feature Correlation Matrix")

corr = df.corr()

st.dataframe(
    corr.style.background_gradient(cmap="Blues")
)

# Model Evaluation
st.subheader("📈 Model Performance Comparison")

results = []

for name, model in models.items():

    y_pred = model.predict(X_test)

    results.append({
        "Model": name,
        "MSE": round(mean_squared_error(y_test, y_pred), 2),
        "MAE": round(mean_absolute_error(y_test, y_pred), 2),
        "R² Score": round(r2_score(y_test, y_pred), 4)
    })

results_df = pd.DataFrame(results)

st.dataframe(results_df, use_container_width=True)

best_model = results_df.loc[
    results_df["R² Score"].idxmax(),
    "Model"
]

st.success(f"🏆 Best Performing Model: {best_model}")

# Actual vs Predicted
st.subheader("📉 Actual vs Predicted Prices")

predictions = models[best_model].predict(X_test)

comparison_df = pd.DataFrame({
    "Actual": y_test.values[:50],
    "Predicted": predictions[:50]
})

st.line_chart(comparison_df)

# Tabs
tab1, tab2 = st.tabs(["Predict Price", "Download Model"])

# Prediction Tab
with tab1:

    model_choice = st.selectbox(
        "Select Model",
        list(models.keys())
    )

    st.write(
        "Enter 13 values separated by commas "
        "(CRIM, ZN, INDUS, CHAS, NOX, RM, AGE, DIS, "
        "RAD, TAX, PTRATIO, B, LSTAT)"
    )

    user_input = st.text_input(
        "Example: 0.1,18,2.3,0,0.5,6.0,65,4.0,1,300,15,396,4.0"
    )

    if st.button("Predict"):

        try:

            values = [float(x.strip()) for x in user_input.split(",")]

            if len(values) != 13:
                st.error("Please enter exactly 13 values.")

            else:

                prediction = models[model_choice].predict([values])[0]

                st.success(
                    f"🏡 Predicted House Price: ₹{prediction*1000:,.2f}"
                )

        except:
            st.error("Invalid input. Please enter numeric values.")

# Download Model Tab
with tab2:

    selected_model = st.selectbox(
        "Choose Model",
        list(models.keys())
    )

    if st.button("Download Model"):

        with open("trained_model.pkl", "wb") as f:
            pickle.dump(models[selected_model], f)

        with open("trained_model.pkl", "rb") as f:
            model_data = f.read()

        b64 = base64.b64encode(model_data).decode()

        href = f'<a href="data:file/pkl;base64,{b64}" download="trained_model.pkl">✅ Download Trained Model</a>'

        st.markdown(href, unsafe_allow_html=True)
