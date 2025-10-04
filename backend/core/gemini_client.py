"""
Google Gemini API Client Configuration
Provides a singleton wrapper for the Gemini API to be used across the application
"""

import os
import asyncio
from typing import Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Global Gemini client instance
_gemini_client: Optional[genai.Client] = None

# Rate limit delay (in seconds) to avoid hitting free tier limits
RATE_LIMIT_DELAY = 8


def configure_gemini():
    """
    Configure the Gemini API with the API key from environment variables
    Should be called once during application startup
    """
    global _gemini_client
    
    if _gemini_client is not None:
        return

    api_key = "AIzaSyCwd9aklnkI9F-YBzirIBTlINASEH0W16E"  # i hardcoded for testing
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    _gemini_client = genai.Client(api_key=api_key)
    print("✅ Gemini API configured successfully")


def get_gemini_client() -> genai.Client:
    """
    Get or create a Gemini Client instance
    
    Returns:
        A configured Client instance
    
    Raises:
        ValueError: If Gemini API is not configured
    """
    global _gemini_client
    
    if _gemini_client is None:
        configure_gemini()
    
    return _gemini_client


def create_schema(schema_type, properties: dict = None, required: list = None):
    """
    Helper function to create a genai.types.Schema object
    
    Args:
        schema_type: genai.types.Type (e.g., Type.OBJECT, Type.STRING, Type.INTEGER)
        properties: Dict of property name to Schema objects (for OBJECT type)
        required: List of required property names (for OBJECT type)
    
    Returns:
        genai.types.Schema object
    
    Example:
        # Simple schema
        string_schema = create_schema(genai.types.Type.STRING)
        
        # Object schema
        person_schema = create_schema(
            genai.types.Type.OBJECT,
            properties={
                "name": create_schema(genai.types.Type.STRING),
                "age": create_schema(genai.types.Type.INTEGER),
            },
            required=["name", "age"]
        )
    """
    from google.genai import types as genai_types
    
    schema_params = {"type": schema_type}
    
    if properties:
        schema_params["properties"] = properties
    
    if required:
        schema_params["required"] = required
    
    return genai_types.Schema(**schema_params)


async def generate_structured_content(
    prompt: str,
    response_schema,  # genai.types.Schema object
    system_instruction: str = None,
    model_name: str = "gemini-flash-latest",
    temperature: float = 0.2
) -> str:
    """
    Generate structured JSON content using Gemini API
    
    Args:
        prompt: The input prompt for content generation
        response_schema: A genai.types.Schema object defining the expected output structure
        system_instruction: Optional system prompt to guide the model's behavior
        model_name: The Gemini model to use
        temperature: Temperature for generation (default: 0.2)
    
    Returns:
        str: The generated content as JSON string matching the response schema
    
    Example:
        schema = genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=["name", "age"],
            properties={
                "name": genai.types.Schema(type=genai.types.Type.STRING),
                "age": genai.types.Schema(type=genai.types.Type.INTEGER),
            }
        )
        result = await generate_structured_content("Generate a person", schema)
    """
    client = get_gemini_client()
    
    # Create content with the prompt
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    
    # Configure generation with JSON schema
    config_params = {
        "temperature": temperature,
        "thinking_config": types.ThinkingConfig(thinking_budget=0),
        "response_mime_type": "application/json",
        "response_schema": response_schema,
        "safety_settings": [
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_NONE",
            ),
        ],
    }
    
    # Add system instruction if provided
    if system_instruction:
        config_params["system_instruction"] = [
            types.Part.from_text(text=system_instruction)
        ]
    
    generate_content_config = types.GenerateContentConfig(**config_params)
    
    # Generate content (non-streaming)
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=generate_content_config,
    )
    
    # Add delay to avoid rate limiting
    await asyncio.sleep(RATE_LIMIT_DELAY)
    
    return response.text


async def generate_conversational_response(
    prompt: str,
    system_instruction: str = None,
    model_name: str = "gemini-flash-latest",
    temperature: float = 0.7
) -> str:
    """
    Generate a conversational response using Gemini API
    
    Args:
        prompt: The input prompt/question
        system_instruction: Optional system prompt to guide the model's behavior
        model_name: The Gemini model to use
        temperature: Temperature for generation (default: 0.7 for more creative responses)
    
    Returns:
        str: The generated response
    
    Example:
        response = await generate_conversational_response(
            "What is the capital of France?",
            system_instruction="You are a helpful geography teacher."
        )
    """
    client = get_gemini_client()
    
    # Create content
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    
    # Configure generation
    config_params = {
        "temperature": temperature,
        "thinking_config": types.ThinkingConfig(thinking_budget=0),
    }
    
    # Add system instruction if provided
    if system_instruction:
        config_params["system_instruction"] = [
            types.Part.from_text(text=system_instruction)
        ]
    
    generate_content_config = types.GenerateContentConfig(**config_params)
    
    # Generate content
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=generate_content_config,
    )
    
    # Add delay to avoid rate limiting
    await asyncio.sleep(RATE_LIMIT_DELAY)
    
    return response.text


async def generate_conversational_response_with_history(
    history: list,
    system_prompt: str,
    model_name: str = "gemini-flash-latest",
    temperature: float = 0.7
) -> str:
    """
    Generate a conversational response based on chat history
    
    Args:
        history: List of previous messages in the conversation
                 Format: [{"speaker": "agent", "message": "Hello"}, ...]
        system_prompt: The system prompt defining the agent's behavior
        model_name: The Gemini model to use
        temperature: Temperature for generation
    
    Returns:
        str: The generated response
    
    Example:
        history = [
            {"speaker": "user", "message": "Hi there!"},
            {"speaker": "agent", "message": "Hello! How can I help?"},
            {"speaker": "user", "message": "Tell me about AI"}
        ]
        response = await generate_conversational_response_with_history(
            history, "You are a helpful AI assistant"
        )
    """
    client = get_gemini_client()
    
    # Format the conversation history into the prompt
    conversation_text = "Conversation History:\n"
    for msg in history:
        speaker = msg.get("speaker", "unknown")
        message = msg.get("message", "")
        conversation_text += f"{speaker}: {message}\n"
    
    conversation_text += "\nPlease provide the next response:"
    
    # Create content
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=conversation_text)],
        ),
    ]
    
    # Configure with system instruction
    generate_content_config = types.GenerateContentConfig(
        temperature=temperature,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        system_instruction=[
            types.Part.from_text(text=system_prompt)
        ],
    )
    
    # Generate content
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=generate_content_config,
    )
    
    # Add delay to avoid rate limiting
    await asyncio.sleep(RATE_LIMIT_DELAY)
    
    return response.text


async def generate_next_turn_with_proper_history(
    contents_history: list,  # List of types.Content objects
    system_prompt: str,
    model_name: str = "gemini-flash-latest",
    temperature: float = 0.7
) -> str:
    """
    Generate the next turn in a conversation using proper Google Genai SDK pattern.
    This function maintains conversation history as a Contents array and keeps
    the system prompt separate, preventing context mixing.
    
    Args:
        contents_history: List of types.Content objects representing the conversation
                         Each Content should have role="user" or role="model"
                         Can be empty for the first turn
        system_prompt: The system prompt defining the speaker's behavior
        model_name: The Gemini model to use
        temperature: Temperature for generation
    
    Returns:
        str: The generated response
    
    Example:
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text="Hello")]
            ),
            types.Content(
                role="model",
                parts=[types.Part.from_text(text="Hi there!")]
            )
        ]
        response = await generate_next_turn_with_proper_history(
            contents, "You are a helpful assistant"
        )
    """
    client = get_gemini_client()
    
    # If history is empty, create a simple prompt to start the conversation
    if not contents_history:
        contents_history = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text="Begin the conversation.")]
            )
        ]
    
    # Configure with system instruction separate from conversation history
    generate_content_config = types.GenerateContentConfig(
        temperature=temperature,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_NONE",
            ),
        ],
        system_instruction=[
            types.Part.from_text(text=system_prompt)
        ],
    )
    
    # Log request details
    print(f"\n{'='*80}")
    print(f"🔍 GEMINI API REQUEST")
    print(f"{'='*80}")
    print(f"📝 Model: {model_name}")
    print(f"🌡️  Temperature: {temperature}")
    print(f"📋 System Prompt (first 200 chars): {system_prompt[:200]}...")
    print(f"📚 History Length: {len(contents_history)} messages")
    if contents_history:
        print(f"📖 Last message in history: {contents_history[-1].parts[0].text[:100]}...")
    print(f"{'='*80}\n")
    
    # Generate content using streaming (more reliable than non-streaming)
    response_text = ""
    chunk_count = 0
    all_chunks_data = []  # Store chunk data for detailed analysis
    
    try:
        for chunk in client.models.generate_content_stream(
            model=model_name,
            contents=contents_history,
            config=generate_content_config,
        ):
            chunk_count += 1
            
            # Store chunk data
            chunk_data = {
                'chunk_number': chunk_count,
                'has_text': hasattr(chunk, 'text'),
                'text_value': chunk.text if hasattr(chunk, 'text') else None,
                'has_candidates': hasattr(chunk, 'candidates'),
                'attributes': dir(chunk)
            }
            
            # Log each chunk received
            print(f"📦 Chunk {chunk_count} received")
            
            # Check if chunk has text
            if hasattr(chunk, 'text') and chunk.text:
                print(f"   ✅ Has text: {chunk.text[:100]}{'...' if len(chunk.text) > 100 else ''}")
                response_text += chunk.text
                chunk_data['text_length'] = len(chunk.text)
            else:
                print(f"   ⚠️  Chunk has no text attribute or text is empty")
                chunk_data['text_length'] = 0
            
            # Check for candidates and safety ratings
            if hasattr(chunk, 'candidates') and chunk.candidates:
                chunk_data['candidates_count'] = len(chunk.candidates)
                for i, candidate in enumerate(chunk.candidates):
                    print(f"   🛡️  Candidate {i} safety ratings:")
                    candidate_info = {}
                    
                    if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                        safety_info = {}
                        for rating in candidate.safety_ratings:
                            rating_str = f"{rating.category}: {rating.probability}"
                            print(f"      - {rating_str}")
                            safety_info[str(rating.category)] = str(rating.probability)
                        candidate_info['safety_ratings'] = safety_info
                    
                    if hasattr(candidate, 'finish_reason'):
                        print(f"   🏁 Finish reason: {candidate.finish_reason}")
                        candidate_info['finish_reason'] = str(candidate.finish_reason)
                    
                    if hasattr(candidate, 'content') and candidate.content:
                        candidate_info['has_content'] = True
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            candidate_info['parts_count'] = len(candidate.content.parts)
                        else:
                            candidate_info['parts_count'] = 0
                    else:
                        candidate_info['has_content'] = False
                    
                    chunk_data[f'candidate_{i}'] = candidate_info
            else:
                chunk_data['candidates_count'] = 0
                print(f"   ⚠️  Chunk has no candidates")
            
            all_chunks_data.append(chunk_data)
            
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ EXCEPTION DURING CONTENT GENERATION")
        print(f"{'='*80}")
        print(f"Error: {str(e)}")
        print(f"Error Type: {type(e).__name__}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        print(f"{'='*80}\n")
        raise Exception(f"Failed to generate response: {str(e)}")
    
    # Log response summary
    print(f"\n{'='*80}")
    print(f"📊 GEMINI API RESPONSE SUMMARY")
    print(f"{'='*80}")
    print(f"📦 Total chunks received: {chunk_count}")
    print(f"📏 Response length: {len(response_text)} characters")
    if response_text:
        print(f"✅ Response (first 500 chars):\n{response_text[:500]}")
    else:
        print(f"❌ Response is EMPTY!")
        print(f"\n🔍 DETAILED CHUNK ANALYSIS:")
        import json
        print(json.dumps(all_chunks_data, indent=2, default=str))
    print(f"{'='*80}\n")
    
    # Check if we got a valid response
    if not response_text or not response_text.strip():
        print(f"❌ EMPTY RESPONSE DETECTED")
        print(f"   - Response text: '{response_text}'")
        print(f"   - Response text stripped: '{response_text.strip() if response_text else 'None'}'")
        print(f"   - Chunks received: {chunk_count}")
        print(f"\n🔍 ALL CHUNKS DATA:")
        import json
        print(json.dumps(all_chunks_data, indent=2, default=str))
        raise Exception("Gemini API returned empty response. This may be due to safety filters or API issues.")
    
    # Add delay to avoid rate limiting
    await asyncio.sleep(RATE_LIMIT_DELAY)
    
    return response_text.strip()


async def generate_conversational_response_stream(
    prompt: str,
    system_instruction: str = None,
    model_name: str = "gemini-flash-latest",
    temperature: float = 0.7
):
    """
    Generate a conversational response using streaming (for real-time output)
    
    Args:
        prompt: The input prompt/question
        system_instruction: Optional system prompt to guide the model's behavior
        model_name: The Gemini model to use
        temperature: Temperature for generation
    
    Yields:
        str: Chunks of the generated response as they become available
    
    Example:
        async for chunk in generate_conversational_response_stream(
            "Tell me a story",
            system_instruction="You are a creative storyteller."
        ):
            print(chunk, end="")
    """
    client = get_gemini_client()
    
    # Create content
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    
    # Configure generation
    config_params = {
        "temperature": temperature,
        "thinking_config": types.ThinkingConfig(thinking_budget=0),
    }
    
    # Add system instruction if provided
    if system_instruction:
        config_params["system_instruction"] = [
            types.Part.from_text(text=system_instruction)
        ]
    
    generate_content_config = types.GenerateContentConfig(**config_params)
    
    # Generate content with streaming
    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=contents,
        config=generate_content_config,
    ):
        yield chunk.text
    
    # Add delay after streaming completes to avoid rate limiting
    await asyncio.sleep(RATE_LIMIT_DELAY)


def cleanup_gemini():
    """
    Cleanup Gemini client resources
    Called during application shutdown
    """
    global _gemini_client
    _gemini_client = None
    print("✅ Gemini client cleaned up")


# ============================================================================
# SCENARIO GENERATION
# ============================================================================

async def generate_scenario_from_ai(
    personality_name: str,
    personality_description: str,
    personality_system_prompt: str,
    user_brief: str
) -> dict:
    """
    Generate a scenario using AI based on a personality and user brief
    
    This function takes a debtor personality and a situation brief, then uses
    the Gemini API with structured JSON output to generate a realistic scenario
    including a title, detailed backstory, and objective for testing.
    
    Args:
        personality_name: Name of the personality (e.g., "Willful Defaulter")
        personality_description: Short description of the personality
        personality_system_prompt: Full system prompt defining the personality behavior
        user_brief: User's brief description of the situation (e.g., "just lost their job")
    
    Returns:
        dict: A dictionary containing:
            - title (str): AI-generated scenario title
            - backstory (str): Detailed backstory for the debtor
            - objective (str): Goal for the debtor in the conversation
    
    Example:
        result = await generate_scenario_from_ai(
            personality_name="Struggling Parent",
            personality_description="A parent dealing with financial hardship",
            personality_system_prompt="You are a single parent who...",
            user_brief="just lost their job"
        )
        # Returns: {
        #   "title": "Struggling Parent - Job Loss",
        #   "backstory": "This debtor is a single parent who...",
        #   "objective": "Try to negotiate a payment plan while..."
        # }
    """
    # Build the input prompt according to PRD specification
    prompt = f"""Based on the following debtor personality and situation, generate a scenario for a debt collection call.

PERSONALITY NAME: {personality_name}
PERSONALITY DESCRIPTION: {personality_description}
PERSONALITY SYSTEM PROMPT: {personality_system_prompt}

SITUATION BRIEF: {user_brief}

Generate a title, a detailed backstory for the debtor, and a clear objective for them in the upcoming call."""

    # Define the output schema according to PRD specification
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        required=["title", "backstory", "objective"],
        properties={
            "title": types.Schema(type=types.Type.STRING),
            "backstory": types.Schema(type=types.Type.STRING),
            "objective": types.Schema(type=types.Type.STRING),
        }
    )
    
    # Generate the structured content
    result_json = await generate_structured_content(
        prompt=prompt,
        response_schema=response_schema,
        system_instruction="You are an expert at creating realistic debt collection test scenarios. Generate detailed, believable scenarios that will help test the performance of debt collection agents.",
        temperature=0.7  # Higher temperature for more creative scenarios
    )
    
    # Parse and return the JSON response
    import json
    return json.loads(result_json)

