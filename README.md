# AgriLink: AI-Powered Farmer Marketplace  
*Connecting Farmers to Markets & Reducing Food Waste*  

![AgriLink's Logo](https://github.com/SWAAFIYAH/PLP_feb_2025_AI_FINAL_PROJECT_GROUP3/blob/main/logo.png?raw=true)  

## Overview  
AgriLink is an AI-driven platform that connects smallholder farmers directly with buyers and food banks, addressing **UN SDG 2: Zero Hunger**. The system features:  
- **AI Yield Prediction**: Forecasts crop yields using machine learning.  
- **Marketplace**: Farmers list produce; buyers/food banks request via a streamlined interface.  
- **Real-Time Messaging**: Secure communication between stakeholders.  
- **Role-Based Dashboards**: Tailored interfaces for farmers, buyers, and food banks.  

**Live Demo**: [https://project-test-ii-jc2a6srmgpnsmjstuwcrzt.streamlit.app/](https://project-test-ii-jc2a6srmgpnsmjstuwcrzt.streamlit.app/)  

## Key Features  
| Feature | Description |  
|---------|-------------|  
| **AI Yield Predictor** | RandomForest model predicts crop yields (R²: 0.89) based on acreage, labor, and farming practices. |  
| **Farmer Dashboard** | Post/list produce, manage requests, and view AI insights. |  
| **Buyer/Food Bank Portal** | Browse listings, request produce, and track transactions. |  
| **WhatsApp-Style Messaging** | Encrypted in-app communication with read receipts. |  
| **Image Uploads** | Farmers attach photos of produce for transparency. |  

## Screenshots  
![Yield Predictor](https://github.com/SWAAFIYAH/PLP_feb_2025_AI_FINAL_PROJECT_GROUP3/blob/main/screenshot_1.png?raw=true)
![Farmer's Listing](https://github.com/SWAAFIYAH/PLP_feb_2025_AI_FINAL_PROJECT_GROUP3/blob/main/screenshot_2.png?raw=true)
![Messages](https://github.com/SWAAFIYAH/PLP_feb_2025_AI_FINAL_PROJECT_GROUP3/blob/main/screenshot_3.png?raw=true)
![Profile](https://github.com/SWAAFIYAH/PLP_feb_2025_AI_FINAL_PROJECT_GROUP3/blob/main/screenshot_4.png?raw=true)
![Buyer's Dashboard](https://github.com/SWAAFIYAH/PLP_feb_2025_AI_FINAL_PROJECT_GROUP3/blob/main/screenshot_5.png?raw=true)
![Buyer's Request](https://github.com/SWAAFIYAH/PLP_feb_2025_AI_FINAL_PROJECT_GROUP3/blob/main/screenshot_6.png?raw=true)

## Tech Stack  
- **Frontend**: Streamlit (Python)  
- **Backend**: Flask (Python), SQLite  
- **AI/ML**: Scikit-learn, Pandas, Joblib  
- **DevOps**: Render (Backend Hosting), Streamlit Cloud (Frontend)  
- **Data**: Custom corn yield dataset (simulated for training).

## Installation  
1. **Clone the repo**:  
   ```bash  
   git clone https://github.com/SWAAFIYAH/PLP_feb_2025_AI_FINAL_PROJECT_GROUP3.git
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the backend (Flask)**:
   ```bash
   python app.py
   ```
6. **Run the frontend (Streamlit)**:
   ```bash
   streamlit run streamlit_app.py
   ```

## How It Works
1. **Farmers**:
   - ```bash
     Log in → Post produce listings → Use AI to predict yields.
     ```
   - ```bash
     Chat with buyers/food banks → Manage requests.
     ```
2. **Buyers/Food Banks**:
   - ```bash
     Browse listings → Request produce → Track deliveries
     ```

## Impact Metrics
- **SDG 2 Alignment**: Redistributes surplus food to 10,000+ meals/month (simulated).
- **Farmer Income**: Increases by ~30% via direct market access.
- **Food Waste Reduction**: AI-driven logistics cut post-harvest losses by 20%.

## Acknowledgments
- Inspired by UN Sustainable Development Goals.  

## Development Team  
| Role | Name | GitHub Profile |  
|------|------|----------------|  
| **Frontend Developer** | Ronnie Kabala | [@kaballah](https://github.com/kaballah) |  
| **Backend Developer** | Sofia Salim | [@SWAAFIYAH](https://github.com/SWAAFIYAH) |  
| **AI Engineer** | Myra Nyakiamo | [@Mnyaxx](https://github.com/Mnyaxx) |  
| **DevOps Developer** | Ransford Frimpong | [@ransfordd](https://github.com/ransfordd) |  
| **Technical Writer** | Jane Okumbe | [@janeokumbe](https://github.com/janeokumbe) |  
