from openai import OpenAI
import requests
import json
import logging
from typing import Optional, Dict, Any, List
from config import HF_API_KEY

logger = logging.getLogger(__name__)

class LLMService:
    # def __init__(self,model="mistralai/Mistral-7B-Instruct-v0.2"):
    #     self.api_url = f"https://router.huggingface.co/v1{model}"
    #     self.headers = {
    #         "Authorization": f"Bearer {HF_API_KEY}",
    #         "Content-Type": "application/json"  }
    def __init__(self, model="deepseek-ai/DeepSeek-V3.2"):
      
        self.model = model
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=HF_API_KEY,
        )
        
        logger.info(f"LLM Service initialized with Hugging Face Router")
        logger.info(f"Model: {model}")

    # def generate_text(self, prompt: str, max_length: int = 200) -> str:
    #     """Generate text using the LLM model."""
    #     payload = {
    #         "inputs": prompt,
    #         "parameters": {
    #             "max_new_tokens": max_length,
    #             "temperature": 0.7,
    #             "top_p": 0.9,
    #             "repetition_penalty": 1.2
    #         }
    #     }
    #     try:
    #         response = requests.post(self, data=json.dumps(payload),timeout=60)
    #         if response.status_code == 200:
    #             result = response.json()
    #             if isinstance(result,list) and 'generated_text' in result[0]:
    #                 text = result[0]["generated_text"]
    #                 if prompt in text:
    #                  text = text.replace(prompt, "").strip()
    #                 return text
    #             else:
    #                 return result[0]["text"].strip() if "text" in result[0] else ""
    #         else:
    #             logger.error(f"LLM API Error {response.status_code}: {response.text}")
    #             return  self._fallback_response(prompt)
    #     except requests.RequestException as e:
    #         logger.error(f"Request Exception: {str(e)}")
    #         return self._fallback_response(prompt)
    def generate_text(self, prompt: str, max_length: int = 500) -> str:
        """Generate text using the LLM model via OpenAI-compatible API."""
        try:
            logger.info(f"Sending request to Hugging Face Router")
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates structured content in JSON format when requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_length,
                # prompt=prompt,
                temperature=0.7,
                top_p=0.9
            )
            
            # Extract text from response
            text = completion.choices[0].message.content
            
            logger.info(f"✅ Generated {len(text)} characters")
            return text.strip()
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM API Error: {error_msg}")
            
            if "401" in error_msg or "authentication" in error_msg.lower():
                logger.error(" Invalid API Key - check your .env file")
            elif "503" in error_msg or "loading" in error_msg.lower():
                logger.warning("⏳ Model is loading, please wait...")
                import time
                time.sleep(20)
                try:
                    return self.generate_text(prompt, max_length)
                except:
                    pass
            elif "429" in error_msg:
                logger.error("Rate limit - wait a moment")
            
            return self._fallback_response(prompt)

    # def generate_lead_magnet_ideas(self, business_description: str) -> List[Dict[str, Any]]:
        # """Generate lead magnet ideas based on business description."""
        # prompt = f"""
        # Generate 3 unique lead magnet ideas for the following business description: {business_description}.
        # For each idea, provide the following details in JSON format:
        # BUSINESS DESCRIPTION:
        # - title: A catchy title for the lead magnet.
        # - type: Type of lead magnet (checklist, template, calculator, report).
        # - value_promise: A brief description of the value it offers.
        # - conversion_score: An integer score (1-10) indicating its potential to convert leads.
        # - format_recommendation: Recommended format (PDF, interactive tool, etc.).
        # Return the ideas as a JSON array in the following format:
        # [
        #     {{
        #         "title": "Lead Magnet Title",
        #         "type": "checklist/template/calculator/report",
        #         "value_promise": "Brief description of value",
        #         "conversion_score": integer (1-10),
        #         "format_recommendation": "Recommended format"
        #     }},
        # ]
        
        # """
        # response = self.generate_text(prompt, max_length=500)
        # try:
        #     json_str = self._extract_json(response)
        #     ideas = json.loads(json_str)

        #     if not isinstance(ideas, list):
        #         raise json.JSONDecodeError("Expected a list of ideas", json_str, 0)
        #     valid_ideas = []
        #     for idea in ideas:
        #         validated = self._validate_idea(idea)
        #         if validated:
        #             valid_ideas.append(validated)
        #     if valid_ideas:
        #         return valid_ideas
        #     logger.warning("llm returned invalid ideas, using fallback")
        #     return self._fallback_response(prompt)
        # except json.JSONDecodeError as e:
        #     logger.error(f"JSON parsing error: {e}")
        #     return self._fallback_response(prompt)

        # return ideas

    def generate_lead_magnet_ideas(
        self,
        icp_profile: str,
        pain_points: List[str],
        content_topics: List[str],
        offer_type: str,
        brand_voice: str,
        conversion_goal: str
    ) -> List[Dict[str, Any]]:
        """Generate structured lead magnet ideas"""
        prompt = f"""You are a lead magnet expert. Generate 3 lead magnet ideas.

TARGET AUDIENCE: {icp_profile}
THEIR PAIN POINTS: {', '.join(pain_points)}
CONTEXT: {', '.join(content_topics)}
BUSINESS TYPE: {offer_type}
BRAND VOICE: {brand_voice}
GOAL: {conversion_goal}

For each idea, provide:
1. title - Catchy name (4-6 words)
2. type - One of: checklist, template, calculator, report
3. value_promise - Clear benefit (1 sentence)
4. conversion_score - 1-10 based on pain point match
5. format_recommendation - Specific format details

Format as JSON array. Example:
[
  {{
    "title": "Client Getter Checklist",
    "type": "checklist",
    "value_promise": "Get 10 high-paying clients in 30 days",
    "conversion_score": 9,
    "format_recommendation": "PDF with 7 actionable steps"
  }}
]

Now generate 3 ideas:"""
        
        response = self.generate_text(prompt, max_length=800)
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Handle different response structures
            if isinstance(data, dict):
                if "ideas" in data:
                    ideas = data["ideas"]
                elif "lead_magnets" in data:
                    ideas = data["lead_magnets"]
                else:
                    ideas = [data]
            elif isinstance(data, list):
                ideas = data
            else:
                ideas = []
            
            # Validate and format ideas
            valid_ideas = []
            for i, idea in enumerate(ideas[:3]):  # Take max 3 ideas
                valid_idea = self._validate_idea(idea, i)
                if valid_idea:
                    valid_ideas.append(valid_idea)
            
            return valid_ideas if valid_ideas else self._generate_fallback_ideas(pain_points, offer_type)
            
        except json.JSONDecodeError:
            # Parse as text if JSON fails
            return self._parse_text_ideas(response, pain_points, offer_type)
    
   
    def generate_checklist(self, title: str, pain_points: List[str]) -> Dict[str, Any]:
        """Generate a checklist for a given topic."""
        prompt = f"""Create a detailed checklist for: {title}
Pain Points to Address: {', '.join(pain_points)}
create 6-11 steps .each step should have:
-step number
-step title (4-6 words)
-step description (1-2 sentences) 
-options time estimates for each step
Format the checklist as JSON:
{{
    "type": "checklist",
    "title": "{title}",
    "steps": [
        {{
            "step": 1,
            "title": "Define Your target audience",
            "description": "Identify who you're helping and what they need."
            "time_estimate": "30 minutes"
        }},
        
    ]
    delivrable: PDF checklist

}}
now generate the checklist:"""
        response = self.generate_text(prompt, max_length=800)
        return self._parse_content_response(response,"checklist", title)
    
     
    def generate_template_content(self, title: str, pain_points: List[str]) -> Dict[str, Any]:
        """Generate template content"""
        prompt = f"""Create a reusable template for: {title}

This helps with: {', '.join(pain_points[:3])}

Create a template with:
1. Clear sections
2. Placeholders in {{brackets}} for customization
3. Example content
4. Instructions for use

Format as JSON:
{{
  "type": "template",
  "title": "{title}",
  "sections": ["Introduction", "Main Content", "Conclusion"],
  "content": "# {{Your Name}}'s {title}\\n\\n## Introduction\\n[Start with...]\\n\\n## Main Content\\n[Add your content...]",
  "format": "Google Docs Template"
}}

Now create the template:"""
        
        response = self.generate_text(prompt, max_length=1000)
        return self._parse_content_response(response, "template", title)
    def generate_calculator_logic(self, title: str, pain_points: List[str]) -> Dict[str, Any]:
        """Generate calculator logic and structure"""
        prompt = f"""Create a calculator for: {title}

This calculates: {', '.join(pain_points[:2])}

Create calculator with:
1. Input fields with labels and types
2. Clear formula or calculation logic
3. Output explanation
4. Example usage

Format as JSON:
{{
  "type": "calculator",
  "title": "{title}",
  "inputs": [
    {{
      "name": "hourly_rate",
      "label": "Your Hourly Rate ($)",
      "type": "number",
      "placeholder": "e.g., 50"
    }}
  ],
  "formula": "total_value = hours_saved * hourly_rate",
  "output": {{
    "label": "Potential Savings",
    "unit": "$"
  }},
  "example": "If you save 10 hours at $50/hour, you save $500"
}}

Now create the calculator:"""
        
        response = self.generate_text(prompt, max_length=800)
        return self._parse_content_response(response, "calculator", title)
    
    def generate_report_content(self, title: str, pain_points: List[str]) -> Dict[str, Any]:
        """Generate report content"""
        prompt = f"""Create a report outline for: {title}

This addresses: {', '.join(pain_points[:3])}

Create report with:
1. Executive summary
2. 3-5 key findings
3. Data/statistics
4. Actionable recommendations
5. Conclusion

Format as JSON:
{{
  "type": "report",
  "title": "{title}",
  "sections": [
    {{
      "title": "Executive Summary",
      "content": "Brief overview of findings..."
    }}
  ],
  "pages": 10,
  "deliverable": "PDF Report"
}}

Now create the report:"""
        
        response = self.generate_text(prompt, max_length=1000)
        return self._parse_content_response(response, "report", title)
    
    def generate_landing_page_copy(self, lead_magnet: Dict[str, Any]) -> Dict[str, Any]:
        """Generate landing page copy"""
        prompt = f"""Create landing page copy for lead magnet:

Title: {lead_magnet.get('title', 'Lead Magnet')}
Type: {lead_magnet.get('type', 'checklist')}
Value: {lead_magnet.get('value_promise', 'Valuable resource')}

Generate:
1. Headline (attention-grabbing)
2. Subheadline (supporting text)
3. 3-4 benefit bullet points
4. Call-to-action button text
5. Form fields (beyond name/email)
6. Thank you page message

Format as JSON:
{{
  "headline": "Get Your Free [Title]",
  "subheadline": "[Value promise explained]",
  "benefits": [
    "Benefit 1: [specific benefit]",
    "Benefit 2: [specific benefit]"
  ],
  "cta": "Download Now",
  "form_fields": ["name", "email", "company", "role"],
  "thank_you_page": "Thank you! Check your email for [title]."
}}

Now create landing page copy:"""
        
        response = self.generate_text(prompt, max_length=600)
        return self._parse_landing_page_response(response, lead_magnet)
    
    def generate_nurture_emails(self, lead_magnet: Dict[str, Any], num_emails: int = 5) -> List[Dict[str, str]]:
        """Generate email nurture sequence"""
        prompt = f"""Create a {num_emails}-email nurture sequence for:

Lead Magnet: {lead_magnet.get('title', 'Resource')}
Value: {lead_magnet.get('value_promise', 'Helps you achieve results')}

Sequence structure:
Email 1: Welcome + deliver lead magnet
Email 2-4: Provide additional value, tips, insights
Email {num_emails}: Soft pitch for related offer

For each email provide:
- sequence_number (1-{num_emails})
- subject (engaging, not spammy)
- body (friendly, helpful, personalized with {{name}})

Format as JSON array.

Now create the email sequence:"""
        
        response = self.generate_text(prompt, max_length=1200)
        return self._parse_email_sequence(response, num_emails)
    #helper function to validate idea
    def _parse_content_response(self, response: str, content_type: str, title: str) -> Dict[str, Any]:
        """Parse content response"""
        try:
            # Try to extract JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            elif "{" in response and "}" in response:
                # Extract first JSON object
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
            else:
                json_str = response.strip()
            
            content = json.loads(json_str)
            content["type"] = content_type
            return content
            
        except json.JSONDecodeError:
            # Create basic structure
            return self._create_fallback_content(content_type, title)
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response in case of API failure."""
        logger.info("Using fallback response.")
        if "lead magnet ideas" in prompt.lower():
            return json.dumps([
                {
                    "title": "Quick Start Success Checklist",
                    "type": "checklist",
                    "value_promise": "Step-by-step guide to get started faster",
                    "conversion_score": 8,
                    "format_recommendation": "PDF download"
                },
                {
                    "title": "Time-Saving Template Pack",
                    "type": "template",
                    "value_promise": "Ready-to-use templates that save hours",
                    "conversion_score": 7,
                    "format_recommendation": "Editable documents"
                },
                {
                    "title": "ROI Calculator Tool",
                    "type": "calculator",
                    "value_promise": "Calculate your potential results instantly",
                    "conversion_score": 9,
                    "format_recommendation": "Interactive web tool"
                }
            ])
        
        return json.dumps({
            "type": "checklist",
            "title": "Quick Start Guide",
            "steps": [
                {"step": 1, "title": "Define Your Goal", "description": "What do you want to achieve?"},
                {"step": 2, "title": "Identify Your Audience", "description": "Who are you helping?"},
                {"step": 3, "title": "Create Your Solution", "description": "Develop your offer."},
                {"step": 4, "title": "Build Your Resource", "description": "Create the content."},
                {"step": 5, "title": "Test and Refine", "description": "Get feedback."}
            ]
        })
    
    def _extract_json(self, response_text: str) -> str:
        """Extract JSON from the response text."""
        try:
            start = response_text.index("[")
            end = response_text.rindex("]") + 1
            return response_text[start:end]
        except ValueError:
            return ""

    def _validate_idea(self, idea: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """Validate and clean idea structure"""
        try:
            # Ensure required fields
            title = idea.get("title") or idea.get("name") or f"Lead Magnet {index + 1}"
            
            # Validate type
            valid_types = ["checklist", "template", "calculator", "report"]
            idea_type = idea.get("type", "").lower()
            if idea_type not in valid_types:
                idea_type = "checklist"  # Default
            
            # Ensure conversion score is valid
            score = idea.get("conversion_score", 7)
            if not isinstance(score, int) or score < 1 or score > 10:
                score = min(max(int(score) if isinstance(score, (int, float)) else 7, 1), 10)
            
            return {
                "title": str(title),
                "type": idea_type,
                "value_promise": idea.get("value_promise") or idea.get("description") or f"Solve your problems with this {idea_type}",
                "conversion_score": score,
                "format_recommendation": idea.get("format_recommendation") or idea.get("format") or f"Downloadable {idea_type}"
            }
        except:
            return None
    
    def _parse_text_ideas(self, text: str, pain_points: List[str], offer_type: str) -> List[Dict[str, Any]]:
        """Parse text response into ideas"""
        ideas = []
        lines = text.strip().split('\n')
        
        current_idea = {}
        for line in lines:
            line = line.strip()
            
            if line.lower().startswith("title:") or line.lower().startswith("name:"):
                if current_idea:
                    ideas.append(self._validate_idea(current_idea, len(ideas)))
                    current_idea = {}
                title = line.split(":", 1)[1].strip()
                current_idea["title"] = title
            
            elif line.lower().startswith("type:"):
                idea_type = line.split(":", 1)[1].strip().lower()
                current_idea["type"] = idea_type
            
            elif line.lower().startswith("value:") or line.lower().startswith("promise:"):
                value = line.split(":", 1)[1].strip()
                current_idea["value_promise"] = value
            
            elif line.lower().startswith("score:") or line.lower().startswith("conversion:"):
                score_text = line.split(":", 1)[1].strip()
                try:
                    current_idea["conversion_score"] = int(''.join(filter(str.isdigit, score_text))[:2])
                except:
                    current_idea["conversion_score"] = 7
        
        if current_idea:
            ideas.append(self._validate_idea(current_idea, len(ideas)))
        
        return ideas if ideas else self._generate_fallback_ideas(pain_points, offer_type)
    def _parse_landing_page_response(self, response: str, lead_magnet: Dict[str, Any]) -> Dict[str, Any]:
        """Parse landing page response"""
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            elif "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            
            # Ensure required fields
            data["headline"] = data.get("headline") or f"Get Your Free {lead_magnet.get('title', 'Resource')}"
            data["cta"] = data.get("cta") or "Download Now"
            data["form_fields"] = data.get("form_fields") or ["name", "email", "company"]
            data["thank_you_page"] = data.get("thank_you_page") or f"Thank you! Check your email for {lead_magnet.get('title', 'your resource')}."
            
            return data
            
        except json.JSONDecodeError:
            return self._create_fallback_landing_page(lead_magnet)
    
    def _parse_email_sequence(self, response: str, num_emails: int) -> List[Dict[str, str]]:
        """Parse email sequence response"""
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            elif "[" in response and "]" in response:
                start = response.find("[")
                end = response.rfind("]") + 1
                json_str = response[start:end]
            else:
                json_str = response.strip()
            
            emails = json.loads(json_str)
            
            # Ensure proper structure
            valid_emails = []
            for i, email in enumerate(emails[:num_emails]):
                if isinstance(email, dict):
                    valid_emails.append({
                        "sequence_number": email.get("sequence_number", i + 1),
                        "subject": email.get("subject") or f"Tip {i + 1} for you",
                        "body": email.get("body") or "Check out this helpful tip..."
                    })
            
            return valid_emails
            
        except json.JSONDecodeError:
            return self._create_fallback_emails(num_emails)
    def _generate_fallback_ideas(self, pain_points: List[str], offer_type: str) -> List[Dict[str, Any]]:
        """Generate fallback ideas"""
        pain = pain_points[0] if pain_points else "problem"
        
        return [
            {
                "title": f"Ultimate {pain.title()} Solution Checklist",
                "type": "checklist",
                "value_promise": f"Solve {pain} with this step-by-step guide",
                "conversion_score": 7,
                "format_recommendation": "PDF checklist"
            },
            {
                "title": f"{offer_type.title()} Success Template",
                "type": "template",
                "value_promise": f"Ready-to-use template for better {offer_type}",
                "conversion_score": 6,
                "format_recommendation": "Editable template"
            }
        ]
    
    def _create_fallback_content(self, content_type: str, title: str) -> Dict[str, Any]:
        """Create fallback content"""
        if content_type == "checklist":
            return {
                "type": "checklist",
                "title": title,
                "steps": [
                    {"step": 1, "title": "Step 1: Set Clear Goals", "description": "Define what success looks like."},
                    {"step": 2, "title": "Step 2: Research Your Audience", "description": "Understand who you're helping."},
                    {"step": 3, "title": "Step 3: Create Your Offer", "description": "Develop your solution."},
                    {"step": 4, "title": "Step 4: Build Your Resource", "description": "Create the actual content."},
                    {"step": 5, "title": "Step 5: Test and Launch", "description": "Share with your audience."}
                ],
                "deliverable": "PDF Checklist"
            }
        elif content_type == "template":
            return {
                "type": "template",
                "title": title,
                "sections": ["Introduction", "Main Content", "Conclusion"],
                "content": f"# {title}\n\nFill in your information below.\n\n## Introduction\n[Start here...]\n\n## Main Content\n[Add your content...]\n\n## Conclusion\n[Wrap up...]",
                "format": "Editable Template"
            }
        else:
            return {
                "type": content_type,
                "title": title,
                "content": f"Content for {title}"
            }
    
    def _create_fallback_landing_page(self, lead_magnet: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback landing page"""
        return {
            "headline": f"Get Your Free {lead_magnet.get('title', 'Resource')}",
           "subheadline": lead_magnet.get(
    "value_promise",
    "Valuable resource to help you succeed"
),
            "benefits": [
                "Save time with ready-to-use content",
                "Get actionable steps you can implement immediately",
                "Access expert insights and strategies"
            ],
            "cta": "Download Now",
            "form_fields": ["name", "email", "company"],
            "thank_you_page": f"Thank you! Check your email for {lead_magnet.get('title', 'your resource')}."
        }
    
    def _create_fallback_emails(self, num_emails: int) -> List[Dict[str, str]]:
        """Create fallback email sequence"""
        emails = []
        for i in range(num_emails):
            if i == 0:
                subject = "Welcome! Here's Your Resource"
                body = "Hi {name}, thanks for downloading! Here's your resource..."
            elif i == num_emails - 1:
                subject = "Ready for the Next Step?"
                body = "Now that you've used the resource, are you ready to..."
            else:
                subject = f"Tip {i} for Better Results"
                body = f"Here's an additional tip to help you..."
            
            emails.append({
                "sequence_number": i + 1,
                "subject": subject,
                "body": body
            })
        
        return emails    