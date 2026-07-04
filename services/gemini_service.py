import time
import google.generativeai as genai
from config.settings import settings
from utils.logger import app_logger
from utils.exceptions import GeminiAPIError

class GeminiLLMService:
    """Service to interact with Google's Gemini models securely with retry mechanisms."""
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        
        if not self.api_key or self.api_key == "MY_GEMINI_API_KEY":
            app_logger.warning("No valid GEMINI_API_KEY found in configuration. Running in simulation mode.")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            genai.configure(api_key=self.api_key)

    def call_llm(self, prompt: str, system_instruction: str = None, temperature: float = 0.2) -> str:
        """Calls the Gemini model with a retry mechanism and robust error handling."""
        if self.simulation_mode:
            return self._simulate_response(prompt)
            
        max_retries = 3
        delay = 2
        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=genai.GenerationConfig(temperature=temperature),
                    system_instruction=system_instruction
                )
                response = model.generate_content(prompt)
                if response.text:
                    return response.text
                raise GeminiAPIError("Empty response body returned from Gemini.")
            except Exception as e:
                app_logger.warning(f"Gemini API attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    app_logger.error("All Gemini API retries exhausted.")
                    raise GeminiAPIError(f"Gemini LLM Call Failed: {str(e)}")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
        return "Failed to retrieve response."

    def call_llm_stream(self, prompt: str, system_instruction: str = None, temperature: float = 0.2):
        """Streams response from Gemini for interactive, low-latency UI updates."""
        if self.simulation_mode:
            simulated_text = self._simulate_response(prompt)
            for word in simulated_text.split(" "):
                yield word + " "
                time.sleep(0.05)
            return

        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.GenerationConfig(temperature=temperature),
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            app_logger.error(f"Gemini API streaming exception: {str(e)}")
            raise GeminiAPIError(f"Streaming failed: {str(e)}")

    def _simulate_response(self, prompt: str) -> str:
        """Simulates responses if the API key is not configured yet (ensures robust prototype execution)."""
        app_logger.info("Simulating Gemini API response (No valid API key provided).")
        prompt_lower = prompt.lower()
        
        if "fee" in prompt_lower or "charge" in prompt_lower:
            return (
                "### Greenwood International School Fees (2026-2027)\n\n"
                "Based on our official ERP system database:\n"
                "- **Kindergarten**: Admission fee of **$5,000** (one-time) and **$28,000** per term.\n"
                "- **Grade 1**: Admission fee of **$10,000** (one-time) and **$35,000** per term.\n"
                "- **Grade 5**: Admission fee of **$10,000** (one-time) and **$42,000** per term.\n"
                "*(Note: There are 3 terms per academic year. Tuition includes textbook access. Sibling discounts are available!)*"
            )
        elif "process" in prompt_lower or "how to apply" in prompt_lower or "steps" in prompt_lower:
            return (
                "### Admission Process\n\n"
                "Greenwood International School follows a structured 4-step admission process:\n"
                "1. **Online Application**: Register and submit the form via our portal.\n"
                "2. **Document Verification**: Submit birth certificate, passport photos, and past academic record files.\n"
                "3. **Interactive Session / Evaluation**: informal meeting for KG, or entrance evaluation exam for Grade 1+.\n"
                "4. **Seat Confirmation**: Complete term fee payment upon approval to secure the enrollment.\n\n"
                "The last date for submitting applications for the 2026-2027 term is **August 15, 2026**."
            )
        elif "transport" in prompt_lower or "bus" in prompt_lower:
            return (
                "### Bus Transportation Services\n\n"
                "Greenwood International School operates school buses covering 4 major routes:\n"
                "- **Route A (Downtown)**: $4,500/term. Status: *Available*\n"
                "- **Route B (Highlands)**: $5,500/term. Status: *Available*\n"
                "- **Route C (Eastside)**: $5,000/term. Status: *Limited Seats*\n"
                "- **Route D (West End)**: $6,000/term. Status: *Full*\n\n"
                "All buses are equipped with high-tech real-time GPS tracking and certified adult supervisors."
            )
        elif "timing" in prompt_lower or "hours" in prompt_lower or "schedule" in prompt_lower:
            return (
                "### School Timings\n\n"
                "Our daily schedule is designed for academic rigor and physical health:\n"
                "- **Kindergarten**: 8:30 AM to 12:30 PM (Monday to Friday)\n"
                "- **Grades 1 to 10**: 8:00 AM to 3:00 PM (Monday to Friday)\n"
                "*(Extra-curricular sports activities occur on Selected Saturdays from 9:00 AM to 12:00 PM)*"
            )
        elif "document" in prompt_lower or "require" in prompt_lower:
            return (
                "### Required Admission Documents\n\n"
                "Please have the following scanned records ready for verification:\n"
                "- **Student Birth Certificate** (or valid Passport)\n"
                "- **4 Recent Passport-sized Photographs** of the child\n"
                "- **Previous School Report Cards/Transcripts** (for Grade 1 and above)\n"
                "- **Transfer Certificate (TC)** from the previous school\n"
                "- **Parent Identity Proof** (Aadhaar Card, Passport, or Driver's License)"
            )
        else:
            return (
                "Thank you for contacting the Greenwood International School Admission Desk. "
                "We provide premium inquiry assistance. Our records indicate we have excellent facilities, "
                "highly qualified faculty (1:15 ratio in KG), robust smart classrooms, science and robotics labs, "
                "and synthetic athletic tracks. "
                "How may I assist you further with admission criteria, seat availability, or fees?"
            )
