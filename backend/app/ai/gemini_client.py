from google import genai

from app.core.config import settings


class GeminiClient:
    def __init__(self) -> None:

        self.client = None

        if settings.gemini_api_key:
            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

        # use a currently supported model
        self.model_name = "gemini-2.5-flash"
    
    def generate_text(self, prompt: str) -> str:

        if not self.client:
            return (
                "Gemini API key is not configured. "
                "Add GEMINI_API_KEY to enable AI responses."
            )

        try:

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            if hasattr(response, "text"):
                return response.text

            return str(response)

        except Exception as e:

            print("=" * 60)
            print("GEMINI ERROR")
            print(type(e).__name__)
            print(str(e))
            print("=" * 60)

            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI Service Error: {str(e)}"
            )


gemini_client = GeminiClient()