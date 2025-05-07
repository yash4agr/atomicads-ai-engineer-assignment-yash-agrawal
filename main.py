import streamlit as st
import json
import os
from datetime import datetime

from llm_handler import generate_campaign_content
from ads_api.meta_ads import (
    create_campaign,
    create_ad_set,
    create_ad,
    get_ad_account_id,
    check_api_access
)
from config import load_config

# Load configuration
config = load_config()

# Page configuration
st.set_page_config(
    page_title="AI-Powered Ad Campaign Creator",
    page_icon="🚀",
    layout="wide"
)

# ISO code mapping
COUNTRY_ISO_MAPPING = {
    "USA": "US",
    "UK": "GB",
    "India": "IN",
    "Canada": "CA",
    "Australia": "AU",
    "Germany": "DE",
    "France": "FR",
    "Japan": "JP",
    "Brazil": "BR",
    "Mexico": "MX",
    "Spain": "ES",
    "Italy": "IT"
}

# App title and description
st.title("🧠 AI-Powered Campaign Creator")
st.markdown("""
This tool helps you create advertising campaigns on Meta (Facebook/Instagram) 
using AI to generate campaign content based on your brief.
""")

# Session state initialization
if 'campaign_created' not in st.session_state:
    st.session_state.campaign_created = False
if 'campaign_details' not in st.session_state:
    st.session_state.campaign_details = {}
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}

# Sidebar for API credentials and settings
with st.sidebar:
    st.header("Settings")
    
    # LLM Settings
    st.subheader("LLM Settings")
    llm_api_key = st.text_input("TogetherAI API Key", value=os.environ.get("TOGETHER_API_KEY", ""), type="password")
    llm_model = st.selectbox(
        "LLM Model",
        options=["meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"],
        index=0
    )
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    # Meta API Settings
    st.subheader("Meta Ads API Settings")
    meta_access_token = st.text_input("Meta Access Token", value=os.environ.get("META_ACCESS_TOKEN", ""), type="password")
    facebook_page_id = st.text_input("Facebook Page ID", value=os.environ.get("FACEBOOK_PAGE_ID", ""))

    # Save settings
    if st.button("Save Settings"):
        os.environ["TOGETHER_API_KEY"] = llm_api_key
        os.environ["META_ACCESS_TOKEN"] = meta_access_token
        os.environ["FACEBOOK_PAGE_ID"] = facebook_page_id
        st.success("Settings saved!")
    
    # Check API connection
    if st.button("Check Meta API Connection"):
        if meta_access_token:
            status, message = check_api_access(meta_access_token)
            if status:
                st.success(f"Connected successfully! {message}")
            else:
                st.error(f"Connection failed: {message}")
        else:
            st.warning("Please enter a Meta access token first")

# Main form for campaign creation
with st.expander("Campaign Brief", expanded=not st.session_state.campaign_created):
    with st.form("campaign_form"):
        # Basic campaign information
        st.subheader("Basic Information")
        business_name = st.text_input("Business Name")
        business_description = st.text_area("Business Description", height=100)
        
        # Campaign details
        st.subheader("Campaign Details")
        campaign_name = st.text_input("Campaign Name", 
                                     value=f"{business_name} Campaign {datetime.now().strftime('%Y-%m-%d')}" if business_name else "")
        campaign_objective = st.selectbox(
            "Campaign Objective",
            options=["AWARENESS", "CONSIDERATION", "CONVERSIONS"],
            index=1
        )
        
        # Target audience
        st.subheader("Target Audience")
        target_age_min = st.number_input("Minimum Age", min_value=18, max_value=65, value=25)
        target_age_max = st.number_input("Maximum Age", min_value=18, max_value=65, value=45)
        target_genders = st.multiselect(
            "Gender",
            options=["ALL", "MALE", "FEMALE"],
            default=["ALL"]
        )
        target_locations = st.multiselect("Location (Country)",
            options=list(COUNTRY_ISO_MAPPING.keys()),
            default=["USA", "India"]
        )
        target_locations = [COUNTRY_ISO_MAPPING[country] for country in target_locations]
        target_locations = list(set(target_locations))
        
        # Ad details
        st.subheader("Ad Creative Brief")
        product_or_service = st.text_input("Product or Service Name")
        key_selling_points = st.text_area("Key Selling Points (one per line)", height=100)
        target_audience_description = st.text_area("Describe your target audience", height=100)
        call_to_action = st.selectbox(
            "Call to Action",
            options=["LEARN_MORE", "SIGN_UP", "SHOP_NOW", "CONTACT_US", "SUBSCRIBE"],
            index=0
        )
        website_url = st.text_input("Landing Page URL", value="https://")
        
        # Budget
        st.subheader("Budget")
        daily_budget = st.number_input("Daily Budget (INR)", min_value=85.0, max_value=1000.0, value=85.0, step=5.0)
        
        # Submit form
        submitted = st.form_submit_button("Generate Campaign")
        
        if submitted:
            # Check for required fields
            if not business_name or not product_or_service or not key_selling_points:
                st.error("Please fill in all required fields")
            else:
                # Prepare campaign brief
                campaign_brief = {
                    "business_name": business_name,
                    "business_description": business_description,
                    "product_or_service": product_or_service,
                    "key_selling_points": key_selling_points,
                    "target_audience": {
                        "age_range": f"{target_age_min}-{target_age_max}",
                        "gender": target_genders[0] if target_genders else "ALL",
                        "locations": target_locations,
                        "description": target_audience_description
                    },
                    "campaign_objective": campaign_objective,
                    "call_to_action": call_to_action
                }
                
                # Show loading state
                with st.spinner("Generating campaign content with AI..."):
                    try:
                        # Generate campaign content using LLM
                        generated_content = generate_campaign_content(
                            campaign_brief=campaign_brief,
                            model=llm_model,
                            temperature=temperature
                        )
                        
                        st.session_state.generated_content = generated_content
                        st.session_state.campaign_details = {
                            "campaign_name": campaign_name,
                            "campaign_objective": campaign_objective,
                            "daily_budget": daily_budget,
                            "website_url": website_url,
                            "call_to_action": call_to_action,
                            "target_audience": {
                                "age_min": target_age_min,
                                "age_max": target_age_max,
                                "genders": target_genders[0] if target_genders else "ALL",
                                "locations": target_locations
                            }
                        }
                        st.success("Campaign content generated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating campaign content: {str(e)}")

# Display generated content if available
if st.session_state.generated_content:
    st.header("Generated Campaign Content")
    
    content = st.session_state.generated_content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ad Headline")
        st.write(content["headline"])
        
        st.subheader("Primary Text")
        st.write(content["primary_text"])
    
    with col2:
        st.subheader("Ad Description")
        st.write(content["description"])
        
        st.subheader("Image Description")
        st.write(content["image_description"])
    
    # Create campaign button
    if not st.session_state.campaign_created:
        if st.button("Create Campaign on Meta"):
            if not meta_access_token:
                st.error("Please enter your Meta access token in the sidebar first")
            elif not facebook_page_id:
                st.error("Please enter your Facebook Page ID in the sidebar first")
            else:
                try:
                    with st.spinner("Creating campaign on Meta..."):
                        # Get ad account ID
                        ad_account_id = get_ad_account_id(meta_access_token)
                        
                        if not ad_account_id:
                            st.error("Could not retrieve ad account ID. Please check your Meta access token.")
                        else:
                            # Create campaign
                            campaign_id = create_campaign(
                                access_token=meta_access_token,
                                ad_account_id=ad_account_id,
                                name=st.session_state.campaign_details["campaign_name"],
                                objective=st.session_state.campaign_details["campaign_objective"],
                                status="PAUSED"  # Start as paused for safety
                            )
                            
                            # Create ad set
                            ad_set_id = create_ad_set(
                                access_token=meta_access_token,
                                ad_account_id=ad_account_id,
                                name=f"{st.session_state.campaign_details['campaign_name']} - Ad Set",
                                campaign_id=campaign_id,
                                daily_budget=st.session_state.campaign_details["daily_budget"],
                                targeting={
                                    "age_min": st.session_state.campaign_details["target_audience"]["age_min"],
                                    "age_max": st.session_state.campaign_details["target_audience"]["age_max"],
                                    "genders": [1] if st.session_state.campaign_details["target_audience"]["genders"] == "MALE" else 
                                              [2] if st.session_state.campaign_details["target_audience"]["genders"] == "FEMALE" else [],
                                    "geo_locations": {"countries": st.session_state.campaign_details["target_audience"]["locations"]}
                                },
                                status="PAUSED"
                            )
                            
                            # Create ad
                            ad_id = create_ad(
                                access_token=meta_access_token,
                                ad_account_id=ad_account_id,
                                name=f"{st.session_state.campaign_details['campaign_name']} - Ad",
                                ad_set_id=ad_set_id,
                                creative_data={
                                    "title": content["headline"],
                                    "body": content["primary_text"],
                                    "description": content["description"],
                                    "image_url": "https://placehold.co/600x400",  # Placeholder image
                                    "website_url": st.session_state.campaign_details["website_url"],
                                    "call_to_action": st.session_state.campaign_details["call_to_action"],
                                    "page_id": facebook_page_id
                                },
                                status="PAUSED"
                            )
                            
                            # Store campaign details in session state
                            st.session_state.campaign_created = True
                            st.session_state.campaign_details.update({
                                "campaign_id": campaign_id,
                                "ad_set_id": ad_set_id,
                                "ad_id": ad_id
                            })
                            
                            st.success("Campaign created successfully on Meta!")
                            st.rerun()
                
                except Exception as e:
                    st.error(f"Error creating campaign: {str(e)}")

# Display campaign details if created
if st.session_state.campaign_created:
    st.header("Campaign Created!")
    st.subheader("Campaign Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Campaign Name:** {st.session_state.campaign_details['campaign_name']}")
        st.write(f"**Campaign ID:** {st.session_state.campaign_details['campaign_id']}")
        st.write(f"**Ad Set ID:** {st.session_state.campaign_details['ad_set_id']}")
        st.write(f"**Ad ID:** {st.session_state.campaign_details['ad_id']}")
    
    with col2:
        st.write(f"**Objective:** {st.session_state.campaign_details['campaign_objective']}")
        st.write(f"**Daily Budget:** ${st.session_state.campaign_details['daily_budget']}")
        st.write(f"**Status:** PAUSED (ready for review)")
        st.write(f"**Facebook Page ID:** {facebook_page_id}")
    
    st.info("""
    Your campaign has been created in a PAUSED state. To launch it:
    1. Log into your Meta Ads Manager
    2. Review the campaign details
    3. Set the campaign status to ACTIVE when ready
    """)
    
    # Reset button
    if st.button("Create Another Campaign"):
        st.session_state.campaign_created = False
        st.session_state.campaign_details = {}
        st.session_state.generated_content = {}
        st.rerun()