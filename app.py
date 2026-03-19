import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ─── Google Sheets Setup ──────────────────────────────────────
SHEET_ID = "1s1D9L6g4mtMaYno94GCMNu91r2HG0_dtd5LQfbM8e1c"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def connect_to_sheet():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    if sheet.row_count == 0 or sheet.cell(1, 1).value is None:
        sheet.append_row([
            "Timestamp", "Name", "Phone", "County", "Age", "Gender",
            "Farm Size (Acres)", "Crop History", "Crop Selected",
            "Soil Type", "Acres Planted", "Fertilizer Recommended"
        ])
    return sheet

# ─── Fertilizer Database ──────────────────────────────────────
recommendations = {
    ("Maize", "Sandy"): {"fertilizer": "DAP + CAN", "amount": "50kg DAP at planting, 50kg CAN at knee-high stage", "tip": "Sandy soils drain fast — split your CAN into 2 applications."},
    ("Maize", "Clay"): {"fertilizer": "DAP + Urea", "amount": "50kg DAP at planting, 30kg Urea after 3 weeks", "tip": "Clay soils retain moisture well. Avoid over-watering after fertilizer application."},
    ("Maize", "Loam"): {"fertilizer": "DAP + CAN", "amount": "50kg DAP at planting, 50kg CAN at tasseling stage", "tip": "Loam is ideal for maize. Maintain proper spacing of 75cm x 25cm."},
    ("Maize", "Acidic"): {"fertilizer": "Lime + DAP + CAN", "amount": "2 tonnes Lime per acre, then 50kg DAP + 50kg CAN", "tip": "Apply lime 2 weeks before planting to neutralize soil acidity first."},
    ("Beans", "Sandy"): {"fertilizer": "TSP (Triple Super Phosphate)", "amount": "25kg TSP per acre at planting", "tip": "Beans fix their own nitrogen. Avoid nitrogen-heavy fertilizers."},
    ("Beans", "Clay"): {"fertilizer": "SSP (Single Super Phosphate)", "amount": "30kg SSP per acre at planting", "tip": "Ensure good drainage in clay soils — waterlogged beans will rot."},
    ("Beans", "Loam"): {"fertilizer": "TSP or DAP (low rate)", "amount": "20kg TSP per acre at planting", "tip": "Loam soil is perfect for beans. Inoculate seeds with rhizobium for better yields."},
    ("Beans", "Acidic"): {"fertilizer": "Lime + TSP", "amount": "1 tonne Lime per acre, then 25kg TSP", "tip": "Beans are very sensitive to acidity. Always correct pH before planting."},
    ("Tomatoes", "Sandy"): {"fertilizer": "NPK 17:17:17 + CAN", "amount": "50kg NPK at planting, 25kg CAN every 3 weeks", "tip": "Sandy soils need frequent feeding. Consider drip irrigation."},
    ("Tomatoes", "Clay"): {"fertilizer": "NPK 17:17:17 + Foliar Feed", "amount": "50kg NPK at planting, foliar spray weekly", "tip": "Stake your tomatoes early and watch for blight in heavy clay soils."},
    ("Tomatoes", "Loam"): {"fertilizer": "NPK 17:17:17 + CAN + Foliar Feed", "amount": "50kg NPK at planting, 30kg CAN at flowering", "tip": "Loam gives best tomato yields. Mulch to retain moisture."},
    ("Tomatoes", "Acidic"): {"fertilizer": "Lime + NPK 17:17:17", "amount": "1.5 tonnes Lime per acre, then 50kg NPK", "tip": "Target soil pH of 6.0–6.8 for tomatoes. Test your soil every season."},
    ("Potatoes", "Sandy"): {"fertilizer": "NPK 23:23:0 + Muriate of Potash", "amount": "50kg NPK at planting, 25kg MOP at tuber initiation", "tip": "Potatoes need potassium for tuber development. Do not skip MOP."},
    ("Potatoes", "Clay"): {"fertilizer": "NPK 23:23:0 + CAN", "amount": "50kg NPK at planting, 30kg CAN at hilling", "tip": "Hill your potatoes well to prevent greening and improve tuber size."},
    ("Potatoes", "Loam"): {"fertilizer": "NPK 23:23:0 + CAN + MOP", "amount": "50kg NPK at planting, 30kg CAN + 25kg MOP at hilling", "tip": "Loam is ideal for potatoes. Rotate crops yearly to prevent disease buildup."},
    ("Potatoes", "Acidic"): {"fertilizer": "Lime + NPK 23:23:0", "amount": "2 tonnes Lime per acre, then 50kg NPK", "tip": "Acidic soils cause potato scab disease. Always lime before planting."},
    ("Wheat", "Sandy"): {"fertilizer": "DAP + CAN", "amount": "40kg DAP at planting, 40kg CAN at tillering", "tip": "Sandy soils may need micro-nutrient supplementation for wheat."},
    ("Wheat", "Clay"): {"fertilizer": "DAP + Urea", "amount": "40kg DAP at planting, 30kg Urea at tillering", "tip": "Ensure proper drainage. Waterlogged wheat develops root rot quickly."},
    ("Wheat", "Loam"): {"fertilizer": "DAP + CAN", "amount": "50kg DAP at planting, 50kg CAN at tillering stage", "tip": "Apply CAN early morning to reduce evaporation losses."},
    ("Wheat", "Acidic"): {"fertilizer": "Lime + DAP + CAN", "amount": "1.5 tonnes Lime per acre, then 40kg DAP + 40kg CAN", "tip": "Wheat grows best at pH 6.0–7.0. Test and correct soil before every season."},
}

# ─── Page Setup ───────────────────────────────────────────────
st.set_page_config(page_title="Fertilizer Advisor", page_icon="🌱", layout="centered")
st.title("🌱 Smart Fertilizer Recommendation App")
st.markdown("### Helping Kenyan Farmers Grow Better Crops")
st.markdown("---")

# ─── SECTION 1: Demographic Information ───────────────────────
st.markdown("## 👤 Section 1: About You")
st.markdown("*This information helps us improve our services for farmers like you.*")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=10, max_value=100, step=1)
with col2:
    phone = st.text_input("Phone Number")
    gender = st.selectbox("Gender", ["Select...", "Male", "Female", "Prefer not to say"])

county = st.selectbox("County", [
    "Select your county...",
    "Baringo","Bomet","Bungoma","Busia","Elgeyo-Marakwet","Embu","Garissa",
    "Homa Bay","Isiolo","Kajiado","Kakamega","Kericho","Kiambu","Kilifi",
    "Kirinyaga","Kisii","Kisumu","Kitui","Kwale","Laikipia","Lamu","Machakos",
    "Makueni","Mandera","Marsabit","Meru","Migori","Mombasa","Murang'a",
    "Nairobi","Nakuru","Nandi","Narok","Nyamira","Nyandarua","Nyeri",
    "Samburu","Siaya","Taita-Taveta","Tana River","Tharaka-Nithi","Trans Nzoia",
    "Turkana","Uasin Gishu","Vihiga","Wajir","West Pokot"
])

st.markdown("---")

# ─── SECTION 2: Farm Information ──────────────────────────────
st.markdown("## 🚜 Section 2: Your Farm Details")

col3, col4 = st.columns(2)
with col3:
    farm_size = st.number_input("Total Farm Size (Acres)", min_value=0.5, max_value=1000.0, step=0.5)
    crop = st.selectbox("🌾 Crop You Want to Plant Now", ["Maize", "Beans", "Tomatoes", "Potatoes", "Wheat"])
with col4:
    crop_history = st.multiselect(
        "Crops You Have Grown Before",
        ["Maize", "Beans", "Tomatoes", "Potatoes", "Wheat", "Sorghum", "Millet", "Cassava", "Sweet Potato", "Kale"]
    )
    soil = st.selectbox("🪱 Your Soil Type", ["Sandy", "Clay", "Loam", "Acidic"])

acres = st.slider("📐 Acres You Are Planting This Season", 1, 20, 1)

st.markdown("---")

# ─── Submit Button ────────────────────────────────────────────
if st.button("🔍 Get My Fertilizer Recommendation", use_container_width=True):

    # Validation
    if not name or not phone or gender == "Select..." or county == "Select your county...":
        st.error("⚠️ Please fill in all your personal details before continuing.")
    else:
        key = (crop, soil)
        result = recommendations.get(key)

        if result:
            # ── Save to Google Sheets ──────────────────────────
            try:
                sheet = connect_to_sheet()
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    name,
                    phone,
                    county,
                    int(age),
                    gender,
                    farm_size,
                    ", ".join(crop_history) if crop_history else "None",
                    crop,
                    soil,
                    acres,
                    result["fertilizer"]
                ])
                st.success("✅ Recommendation Ready! Your information has been saved.")
            except Exception as e:
                st.warning(f"⚠️ Recommendation ready but could not save data: {e}")

            # ── Display Results ────────────────────────────────
            st.markdown(f"### 🌾 Crop: **{crop}** | 🪱 Soil: **{soil} Soil** | 📐 Area: **{acres} acre(s)**")
            st.markdown("---")

            col5, col6 = st.columns(2)
            with col5:
                st.markdown("#### 🧪 Recommended Fertilizer")
                st.info(result["fertilizer"])
            with col6:
                st.markdown("#### ⚖️ Amount Per Acre")
                st.info(result["amount"])

            st.markdown("#### 📦 Total Quantity Needed")
            st.warning(f"Multiply the amounts above by **{acres} acres** to get your total requirement.")

            st.markdown("#### 💡 Farmer's Tip")
            st.success(result["tip"])

        else:
            st.error("No recommendation found. Please contact your local agronomist.")

# ─── Footer ───────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray;'>🌍 Built for Kenyan Farmers | Powered by Smart Agriculture Research</div>",
    unsafe_allow_html=True
)

## Now Run It:

##4. Press **Ctrl + S** to save
##5. In the terminal at the bottom type:
##py -m streamlit run app.py
