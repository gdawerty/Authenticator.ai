import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIClassificationService:
    """
    Service for classifying documents using OpenAI API
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.logger = logging.getLogger(__name__)
        
        # Define the classification categories and subcategories
        self.categories = {
            "Financial": [
                "Bank Statement", "Credit Card Statement", "Invoice", "Receipt",
                "Tax Document", "Investment Statement", "Insurance Document",
                "Loan Document", "Pay Stub", "Budget Document"
            ],
            "Legal": [
                "Contract", "Legal Agreement", "Court Document", "Legal Notice",
                "Power of Attorney", "Will", "Trust Document", "Legal Brief",
                "Compliance Document", "Regulatory Filing"
            ],
            "Medical": [
                "Medical Record", "Prescription", "Lab Report", "Insurance Card",
                "Medical Bill", "Health Certificate", "Vaccination Record",
                "Medical History", "Treatment Plan", "Diagnostic Report"
            ],
            "Educational": [
                "Diploma", "Transcript", "Certificate", "Academic Record",
                "Course Material", "Research Paper", "Thesis", "Assignment",
                "Grade Report", "Enrollment Document"
            ],
            "Government": [
                "ID Card", "Passport", "Driver License", "Birth Certificate",
                "Marriage Certificate", "Social Security Card", "Voter ID",
                "Government Form", "Official Letter", "Permit"
            ],
            "Business": [
                "Business Plan", "Proposal", "Report", "Presentation",
                "Meeting Minutes", "Policy Document", "Procedure Manual",
                "Employee Handbook", "Company Policy", "Business Contract"
            ],
            "Personal": [
                "Personal Letter", "Diary Entry", "Personal Note", "Journal",
                "Personal Photo", "Personal Document", "Personal Record",
                "Personal Correspondence", "Personal Certificate", "Personal ID"
            ],
            "Other": [
                "Unknown Document", "Miscellaneous", "Uncategorized",
                "Mixed Content", "General Document", "Other Type"
            ]
        }
    
    def classify_document(self, text_content: str, confidence_threshold: float = 0.7) -> Dict:
        """
        Classify a document into category and subcategory using OpenAI API
        
        Args:
            text_content (str): The text content of the document to classify
            confidence_threshold (float): Minimum confidence threshold for classification
            
        Returns:
            Dict: Classification result with category, subcategory, confidence, and reasoning
        """
        try:
            # Prepare the classification prompt
            prompt = self._create_classification_prompt(text_content)
            
            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4o-mini for cost efficiency
                messages=[
                    {
                        "role": "system",
                        "content": "You are a document classification expert. Analyze the given text and classify it into the most appropriate category and subcategory from the provided options. Return your response as a valid JSON object."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            classification_result = json.loads(response.choices[0].message.content)
            
            # Validate the response
            validated_result = self._validate_classification_response(classification_result)
            
            # Add metadata
            validated_result.update({
                "model_used": "gpt-4o-mini",
                "api_timestamp": response.created,
                "input_length": len(text_content),
                "confidence_threshold": confidence_threshold
            })
            
            return validated_result
            
        except Exception as e:
            self.logger.error(f"Error in OpenAI classification: {str(e)}")
            return {
                "category": "Other",
                "subcategory": "Unknown Document",
                "confidence": 0.0,
                "reasoning": f"Classification failed due to error: {str(e)}",
                "error": True
            }
    
    def _create_classification_prompt(self, text_content: str) -> str:
        """
        Create the classification prompt for OpenAI API
        
        Args:
            text_content (str): The text content to classify
            
        Returns:
            str: Formatted prompt for OpenAI API
        """
        categories_text = "\n".join([
            f"- {cat}: {', '.join(subcats)}" 
            for cat, subcats in self.categories.items()
        ])
        
        prompt = f"""
Please classify the following document text into the most appropriate category and subcategory from the options below.

Available Categories and Subcategories:
{categories_text}

Document Text:
{text_content[:2000]}...

Please analyze the content and return a JSON response with the following structure:
{{
    "category": "The main category name",
    "subcategory": "The specific subcategory name",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this classification was chosen"
}}

Rules:
1. Choose the most specific and accurate category/subcategory combination
2. Confidence should be between 0.0 and 1.0
3. If uncertain, use "Other" category with appropriate subcategory
4. Reasoning should be concise but informative
5. Return only valid JSON, no additional text
"""
        return prompt
    
    def _validate_classification_response(self, response: Dict) -> Dict:
        """
        Validate and clean the classification response from OpenAI
        
        Args:
            response (Dict): Raw response from OpenAI API
            
        Returns:
            Dict: Validated and cleaned response
        """
        # Ensure required fields exist
        required_fields = ["category", "subcategory", "confidence", "reasoning"]
        for field in required_fields:
            if field not in response:
                response[field] = "Unknown" if field != "confidence" else 0.0
        
        # Validate category
        if response["category"] not in self.categories:
            response["category"] = "Other"
        
        # Validate subcategory
        valid_subcategories = self.categories.get(response["category"], [])
        if response["subcategory"] not in valid_subcategories:
            response["subcategory"] = valid_subcategories[0] if valid_subcategories else "Unknown Document"
        
        # Validate confidence
        try:
            confidence = float(response["confidence"])
            confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
            response["confidence"] = confidence
        except (ValueError, TypeError):
            response["confidence"] = 0.5
        
        # Ensure reasoning is a string
        if not isinstance(response["reasoning"], str):
            response["reasoning"] = str(response["reasoning"])
        
        return response
    
    def get_available_categories(self) -> Dict[str, List[str]]:
        """
        Get all available categories and subcategories
        
        Returns:
            Dict[str, List[str]]: Dictionary of categories and their subcategories
        """
        return self.categories.copy()
    
    def batch_classify_documents(self, text_contents: List[str], 
                                confidence_threshold: float = 0.7) -> List[Dict]:
        """
        Classify multiple documents in batch
        
        Args:
            text_contents (List[str]): List of text contents to classify
            confidence_threshold (float): Minimum confidence threshold
            
        Returns:
            List[Dict]: List of classification results
        """
        results = []
        for i, text_content in enumerate(text_contents):
            try:
                result = self.classify_document(text_content, confidence_threshold)
                result["document_index"] = i
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error classifying document {i}: {str(e)}")
                results.append({
                    "category": "Other",
                    "subcategory": "Unknown Document",
                    "confidence": 0.0,
                    "reasoning": f"Classification failed: {str(e)}",
                    "error": True,
                    "document_index": i
                })
        
        return results
    
    def get_classification_statistics(self, classifications: List[Dict]) -> Dict:
        """
        Get statistics from a list of classifications
        
        Args:
            classifications (List[Dict]): List of classification results
            
        Returns:
            Dict: Statistics about the classifications
        """
        if not classifications:
            return {}
        
        stats = {
            "total_documents": len(classifications),
            "categories": {},
            "subcategories": {},
            "confidence_stats": {
                "mean": 0.0,
                "min": 1.0,
                "max": 0.0
            },
            "errors": 0
        }
        
        total_confidence = 0.0
        valid_classifications = 0
        
        for classification in classifications:
            # Count categories
            category = classification.get("category", "Unknown")
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            
            # Count subcategories
            subcategory = classification.get("subcategory", "Unknown")
            stats["subcategories"][subcategory] = stats["subcategories"].get(subcategory, 0) + 1
            
            # Track confidence
            confidence = classification.get("confidence", 0.0)
            if confidence > 0:
                total_confidence += confidence
                valid_classifications += 1
                stats["confidence_stats"]["min"] = min(stats["confidence_stats"]["min"], confidence)
                stats["confidence_stats"]["max"] = max(stats["confidence_stats"]["max"], confidence)
            
            # Count errors
            if classification.get("error", False):
                stats["errors"] += 1
        
        # Calculate mean confidence
        if valid_classifications > 0:
            stats["confidence_stats"]["mean"] = total_confidence / valid_classifications
        
        return stats
