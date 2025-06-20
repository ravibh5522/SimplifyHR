# ai_hr_jd_project/services/gemini_service.py
from google import genai
from config import Config
from schemas.jd_schemas import JobDescriptionContent, JDGenerateRequest # Import the Pydantic model for structured output

class GeminiService:
    def __init__(self):
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured.")
        client = genai.Client(api_key="GOOGLE_API_KEY")


    def generate_structured_jd(self, jd_input: JDGenerateRequest) -> JobDescriptionContent:
        prompt = f"""
        Act as an expert HR recruitment specialist and a master copywriter.
        Based on the following information, generate a comprehensive and engaging job description.
        The output MUST be a valid JSON object matching the provided schema.

        Job Title to be created: {jd_input.job_title_input}
        Key Responsibilities: {', '.join(jd_input.key_responsibilities_input)}
        Required Skills/Qualifications: {', '.join(jd_input.required_skills_input)}
        Company Description (optional): {jd_input.company_description_input or 'Not provided, create a generic placeholder if needed.'}

        Desired JSON Structure:
        {{
            "job_title": "string (The final job title, can be same as input or refined)",
            "company_summary": "string (Brief summary of the company)",
            "role_summary": "string (Brief summary of the role)",
            "key_responsibilities": ["string", "..."],
            "required_qualifications": ["string", "..."],
            "preferred_qualifications": ["string", "..."],
            "benefits": ["string", "..."]
        }}

        Ensure all fields in the JSON structure are populated appropriately based on the input.
        If some information (like preferred_qualifications or benefits) is not directly provided,
        you can either omit it, provide sensible defaults, or indicate it needs to be filled.
        The job_title in the output JSON should be the one you craft for the JD.
        """
        response = None
        try:
            client = genai.Client(api_key=Config.GOOGLE_API_KEY)
            response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_schema":  JobDescriptionContent,  # Use the Pydantic model schema
    },
)

            # The response.text will be a JSON string.
            # response.candidates[0].content.parts[0].text is also the JSON string
            # If response_schema is used correctly, response.parts[0] should be a FunctionCall for some models or directly data
            # For Gemini 1.5 with native JSON mode, response.text should be the JSON.
            # And response.candidates[0].content.parts[0].text
            # The user's example shows 'response.parsed' - let's assume that's how the SDK handles it
            # when response_schema is provided in the new SDK version.
            # If `response.parsed` doesn't exist, we might need to parse `response.text`
            # For `google-generativeai` version 0.5.0 and above with gemini-1.5-flash:
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                # The .text attribute should contain the JSON string
                # The SDK automatically parses it if response_schema is used
                # However, the user provided `response.parsed`, let's try to align
                # The user's example: `my_recipes: list[Recipe] = response.parsed`
                # So for a single object, it would be `jd_object: JobDescriptionContent = response.parsed`
                # Let's check the type of response and how the SDK populates this.
                # Assuming the SDK directly provides the parsed Pydantic model:

                # According to Gemini docs for `response_schema` in `generation_config`:
                # The model's response will be returned as a `genai.types.GenerateContentResponse`.
                # The `response.text` attribute will contain the raw JSON string.
                # The `response.candidates[0].content.parts[0].text` will also be the JSON string.
                # To get the Pydantic object, you need to parse it yourself if `response.parsed` is not available.

                # Let's try to use the most straightforward way the SDK intends
                # If using `response_schema` in GenerationConfig, the SDK handles parsing.
                # `response.text` is the JSON string. Let's parse it explicitly if needed.
                # However, the user's example `response.parsed` suggests it might be directly available.
                # Let's assume `response.text` is the JSON and parse it with Pydantic.
                
                # Update based on user's sample:
                # The `genai.Client` is older. The current is `genai.GenerativeModel`.
                # The new API for structured output (JSON mode) with `gemini-1.5-flash` or `gemini-1.5-pro`
                # would use `response_mime_type="application/json"` in `generation_config`.
                # The `response_schema` is part of `Tool` definitions or directly in `generation_config` for some models.

                # Let's assume the user's snippet for `genai.Client` implies the SDK version.
                # If `response.parsed` is how that older client SDK worked with schema,
                # then we would use that. But `google-generativeai` library is current.

                # For current `google-generativeai` library (e.g., v0.5+):
                # When `response_mime_type="application/json"` is set in `generation_config`,
                # and you are using a model that supports native JSON output (like gemini-1.5-flash-latest),
                # `response.text` contains the JSON string.
                # `response_schema` in `generation_config` is used to validate the output against Pydantic schema.
                # The SDK then tries to parse `response.text` into the schema if provided.

                # Let's try to make it work assuming modern SDK.
                # If `response_schema` is in `GenerationConfig`, the SDK tries to parse.
                # `response.candidates[0].content.parts[0].text` is the string.
                # We need to parse this string into our Pydantic model.
                
                # Modern SDK for JSON native output:
                # The `response.text` attribute of `GenerateContentResponse` will contain the JSON string.
                # We can then parse this with Pydantic.
                if hasattr(response, 'text') and response.text:
                    parsed_jd = JobDescriptionContent.model_validate_json(response.text)
                    return parsed_jd
                else:
                    # Fallback or error if text is not available or empty
                    # This part might need adjustment based on exact SDK behavior with `response_schema`
                    # For some versions, if schema is used, it might already be parsed.
                    # Check `response.candidates[0].content.parts[0]` if it's already a dict or Pydantic obj
                    first_part = response.candidates[0].content.parts[0]
                    if hasattr(first_part, 'text') and first_part.text is not None:  # Ensure text is not None
                         parsed_jd = JobDescriptionContent.model_validate_json(first_part.text)
                         return parsed_jd
                    # If the SDK does auto-parsing into the schema when provided in GenerationConfig
                    # then the result might be directly in a field like `response.data` or similar.
                    # The user's example `response.parsed` is specific to `genai.Client`.
                    # For `genai.GenerativeModel`, it's usually `response.text`.
                    raise ValueError("Failed to get parsed JSON from Gemini response. Raw response: " + str(response))
        except Exception as e:
            print(f"Error generating JD with Gemini: {e}")
            if response is not None:
                print(f"Gemini raw response (if available): {getattr(response, 'prompt_feedback', '')}")
                # print(f"Gemini raw response parts: {response.candidates[0].content.parts}")
            raise  # Re-raise the exception to be caught by the route
        
        raise ValueError("Gemini response was empty or not in expected format.")
        raise ValueError("Gemini response was empty or not in expected format.")