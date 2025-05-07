import os
import json
import openai
from typing import Dict, Any

def generate_campaign_content(
    campaign_brief: Dict[str, Any],
    model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    temperature: float = 0.7
) -> Dict[str, str]:
    """
    Generate ad campaign content using TogetherAI's LLM.
    
    Args:
        campaign_brief: Dictionary containing campaign details
        model: The TogetherAI model to use
        temperature: Creativity level (0.0-1.0)
        
    Returns:
        Dictionary with generated content (headline, primary_text, description, image_description)
    """
    # Get API key from environment variable
    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("TogetherAI API key not found. Please set the TOGETHER_API_KEY environment variable.")
    
    # Format the prompt
    prompt = create_campaign_prompt(campaign_brief)
    
    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.together.xyz/v1"
        )
        
        # Call the TogetherAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert marketing copywriter specializing in creating engaging ad content for social media platforms."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=1000,
            n=1,
            stop=None
        )
    
        content_text = response.choices[0].message.content
        
        try:
            content = json.loads(content_text)
        except json.JSONDecodeError:
            content = extract_json_from_text(content_text) # If not a valid json
            
        # Validate the content
        validate_content(content)
        
        return content
    
    except Exception as e:
        raise Exception(f"Error generating campaign content: {str(e)}")


def create_campaign_prompt(campaign_brief: Dict[str, Any]) -> str:
    """
    Create a detailed prompt for the LLM based on the campaign brief.
    
    Args:
        campaign_brief: Dictionary containing campaign details
        
    Returns:
        Formatted prompt string
    """
    # Extract details for easier access
    business_name = campaign_brief.get("business_name", "")
    business_description = campaign_brief.get("business_description", "")
    product_or_service = campaign_brief.get("product_or_service", "")
    key_selling_points = campaign_brief.get("key_selling_points", "")
    target_audience = campaign_brief.get("target_audience", {})
    campaign_objective = campaign_brief.get("campaign_objective", "CONSIDERATION")
    call_to_action = campaign_brief.get("call_to_action", "LEARN_MORE")
    
    # Build the prompt
    prompt = f"""
Create engaging ad content for a social media campaign based on the following brief:

BUSINESS INFORMATION:
- Business Name: {business_name}
- Business Description: {business_description}
- Product/Service: {product_or_service}

KEY SELLING POINTS:
{key_selling_points}

TARGET AUDIENCE:
- Age Range: {target_audience.get('age_range', '25-45')}
- Gender: {target_audience.get('gender', 'ALL')}
- Locations: {target_audience.get('locations', 'United States')}
- Description: {target_audience.get('description', '')}

CAMPAIGN OBJECTIVE: {campaign_objective}
CALL TO ACTION: {call_to_action}

Please generate the following content for this ad campaign:
1. A compelling headline (max 40 characters)
2. Primary text (max 125 characters)
3. Ad description (max 30 characters)
4. Image description for the ad creative

Format your response as a JSON object with the following structure:
{{
  "headline": "Your headline here",
  "primary_text": "Your primary text here",
  "description": "Your description here",
  "image_description": "Your image description here"
}}

Keep the content concise, engaging, and aligned with the brand and target audience. Make sure to highlight the key selling points and include a clear call to action.
"""
    
    return prompt


def extract_json_from_text(text: str) -> Dict[str, str]:
    """
    Extract JSON content from a text response that may contain additional text.
    
    Args:
        text: Response text from the LLM
        
    Returns:
        Extracted JSON as a dictionary
    """
    # Try to find JSON content between curly braces
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        json_str = text[start_idx:end_idx+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Remove any markdown code block markers, just in case
            json_str = json_str.replace('```json', '').replace('```', '')
            return json.loads(json_str)
    
    # If no JSON found, return a default structure
    raise ValueError("Could not extract valid JSON from LLM response")


def validate_content(content: Dict[str, str]) -> None:
    """
    Validate that the generated content has all required fields.
    
    Args:
        content: Dictionary with generated content
        
    Raises:
        ValueError: If content is missing required fields
    """
    required_fields = ["headline", "primary_text", "description", "image_description"]
    
    for field in required_fields:
        if field not in content:
            raise ValueError(f"Generated content is missing required field: {field}")