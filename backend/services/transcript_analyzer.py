"""
Transcript Analysis Service using Google Gemini
Analyzes debt collection call transcripts and generates risk matrices
"""

import os
import json
import asyncio
import logging
from typing import Dict, Optional
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class TranscriptAnalyzer:
    """
    Analyzes call transcripts using Google Gemini LLM to generate risk scores
    """
    
    def __init__(self):
        """Initialize the Gemini client with API key from environment"""
        api_key =  "AIzaSyCuZ5iSn1OdPIngPRDggotqDPWNJFHzigg"  # os.getenv("GEMINI_API_KEY") i shold not be be doing this but its for now
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"
        logger.info("TranscriptAnalyzer initialized with Gemini API")
    
    def _format_transcript_for_analysis(self, transcript_data: Dict) -> str:
        """
        Convert transcript JSON to formatted text for LLM analysis
        
        Args:
            transcript_data: Raw transcript JSON with items array
        
        Returns:
            Formatted transcript string with role labels
        """
        formatted_lines = []
        
        for item in transcript_data.get("items", []):
            if item.get("type") == "message":
                role = item.get("role", "unknown")
                content = item.get("content", [])
                
                # Extract text from content array
                if isinstance(content, list):
                    text = " ".join(content)
                else:
                    text = str(content)
                
                # Format as "Role: Text"
                role_label = "Agent" if role == "assistant" else "Customer"
                formatted_lines.append(f"{role_label}: {text}")
        
        return "\n".join(formatted_lines)
    
    async def analyze_transcript(self, transcript_data: Dict) -> Optional[Dict[str, float]]:
        """
        Analyze transcript and generate risk matrices using Gemini LLM
        
        Args:
            transcript_data: Raw transcript JSON from file
        
        Returns:
            Dictionary containing 5 risk scores (1-100 scale), or None if analysis fails
            {
                "loan_recovery_score": float,
                "willingness_to_pay_score": float,
                "escalation_risk_score": float,
                "customer_sentiment_score": float,
                "promise_to_pay_reliability_index": float
            }
        """
        try:
            # Format transcript for LLM analysis
            formatted_transcript = self._format_transcript_for_analysis(transcript_data)
            
            if not formatted_transcript:
                logger.warning("Empty transcript provided for analysis")
                return None
            
            logger.info(f"Analyzing transcript ({len(formatted_transcript)} characters)")
            
            # Define the system instruction for the LLM
            system_instruction = """You are an advanced AI agent tasked with analyzing customer debt collection call transcripts and producing structured risk scores based on deep linguistic and behavioral analysis. Identify, define, and quantify the following risk matrices for each transcript, producing a score between 1 and 100 for each. Higher scores always indicate a more favorable (lower risk) state for the lender/collector.

---

### Matrices to Output

#### 1. **Loan Recovery Score**
- **Definition:** Probability (1-100) of successful loan repayment by the customer inferred from transcript signals.
- **Signals to Consider:**  
  - Explicit or implicit agreement to pay  
  - Commitment level (specific dates, positive intent)  
  - Excuses or delays (vague responses, avoidance)  
  - Historical reliability if referenced  
  - Signs of distress or negative sentiment

#### 2. **Willingness-to-Pay Score**
- **Definition:** Strength (1-100) of customer's willingness, intent, and openness to settling the debt soon.
- **Signals to Consider:**  
  - Positive affirmations ("I will pay", "Let's settle", "How can I pay?")  
  - Negotiation, plan requests  
  - Cooperative tone versus avoidance/hostility  
  - Clarity of payment plan acceptance

#### 3. **Escalation Risk Score**
- **Definition:** Risk (1-100, reverse scale) that this interaction requires escalation (legal, supervisor intervention, hard recovery).
- **Signals to Consider:**  
  - Aggressive, abusive, or frustrated language  
  - Threats, legal warnings, refusal  
  - Persistent avoidance  
  - Repeated delay tactics

#### 4. **Customer Sentiment Score**
- **Definition:** Aggregate customer sentiment throughout the call (1-100: 100 = strongly positive, 1 = strongly negative).
- **Signals to Consider:**  
  - Sentiment/affect detected in all customer utterances  
  - Politeness, apology, cooperation  
  - Negative language, anger, sadness, stress

#### 5. **Promise-to-Pay Reliability Index**
- **Definition:** Score (1-100) estimating likelihood that any explicit payment promises made are genuine and reliable.
- **Signals to Consider:**  
  - Specific vs. vague commitments ("Friday" vs. "soon")  
  - Tone of voice, past references to fulfilled promises  
  - Consistency in responses  
  - Avoidance or changes in statement

---

**Instructions to Agent:**  
- Input: Raw transcript of the customer debt collection call.
- Output: A structured set of five risk matrices (listed above), with each score normalized to between 1 and 100 (100 showing very low risk for collector/lender).
- For each matrix, base your score on a combination of clear linguistic cues, behavioral signals, sentiment, negotiation patterns, historical references (if present), and explicit/implicit statements found anywhere in the transcript.
- Scores must be interpretable individually and together to offer a holistic view of customer risk post interaction.

---

*Do NOT describe the scoring logic in your output. Only provide the structured five-part matrix.*

---"""
            
            # Prepare the content for the LLM
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=formatted_transcript),
                    ],
                ),
            ]
            
            # Configure response format with JSON schema
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    required=[
                        "Loan Recovery Score",
                        "Willingness-to-Pay Score",
                        "Escalation Risk Score",
                        "Customer Sentiment Score",
                        "Promise-to-Pay Reliability Index"
                    ],
                    properties={
                        "Loan Recovery Score": genai.types.Schema(
                            type=genai.types.Type.NUMBER,
                        ),
                        "Willingness-to-Pay Score": genai.types.Schema(
                            type=genai.types.Type.NUMBER,
                        ),
                        "Escalation Risk Score": genai.types.Schema(
                            type=genai.types.Type.NUMBER,
                        ),
                        "Customer Sentiment Score": genai.types.Schema(
                            type=genai.types.Type.NUMBER,
                        ),
                        "Promise-to-Pay Reliability Index": genai.types.Schema(
                            type=genai.types.Type.NUMBER,
                        ),
                    },
                ),
                system_instruction=[
                    types.Part.from_text(text=system_instruction),
                ],
            )
            
            # Generate content using streaming
            response_text = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                response_text += chunk.text
            
            # Add delay to avoid rate limiting (8 seconds)
            await asyncio.sleep(8)
            
            # Parse the JSON response
            scores = json.loads(response_text)
            
            # Normalize field names to snake_case for database storage
            normalized_scores = {
                "loan_recovery_score": float(scores.get("Loan Recovery Score", 0)),
                "willingness_to_pay_score": float(scores.get("Willingness-to-Pay Score", 0)),
                "escalation_risk_score": float(scores.get("Escalation Risk Score", 0)),
                "customer_sentiment_score": float(scores.get("Customer Sentiment Score", 0)),
                "promise_to_pay_reliability_index": float(scores.get("Promise-to-Pay Reliability Index", 0))
            }
            
            logger.info(f"✅ Transcript analysis completed: {normalized_scores}")
            return normalized_scores
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse LLM response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error analyzing transcript: {e}")
            return None


# Global analyzer instance
_analyzer: Optional[TranscriptAnalyzer] = None


def get_analyzer() -> TranscriptAnalyzer:
    """
    Get or create the global TranscriptAnalyzer instance
    
    Returns:
        TranscriptAnalyzer instance
    """
    global _analyzer
    
    if _analyzer is None:
        _analyzer = TranscriptAnalyzer()
    
    return _analyzer
