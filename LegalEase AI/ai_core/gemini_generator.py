import os
from dataclasses import dataclass

from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    genai = None


load_dotenv()


@dataclass
class GeminiDocumentGenerator:
    api_key: str | None = None
    model_name: str | None = None

    def __post_init__(self):
        self.api_key = self.api_key or os.getenv("GEMINI_API_KEY")

        self.model_name = (
            self.model_name
            or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        )

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Please add your Gemini API key to the .env file."
            )

        if genai is None:
            raise RuntimeError(
                "google-genai is not installed. "
                "Run: pip install -r requirements.txt"
            )

        self.client = genai.Client(api_key=self.api_key)

    @staticmethod
    def build_prompt(
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:

        prompt = f"""
You are an AI legal-document drafting assistant.

Create a professional LEGAL DOCUMENT DRAFT using only the information
provided by the user.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{effective_date}

IMPORTANT RULES:

1. Create a clear professional document title.

2. Clearly identify the parties.

3. Include the effective date.

4. Organize the document into numbered sections.

5. Include all important terms supplied by the user.

6. Use professional legal drafting language.

7. Do NOT invent:
   - names
   - addresses
   - dates
   - amounts
   - laws
   - jurisdictions
   - obligations
   - signatures

8. If important information is missing, use a placeholder such as:
   [INSERT ADDRESS]
   [INSERT AMOUNT]
   [INSERT JURISDICTION]

9. Include sections appropriate for the requested document.

10. Add a signature section at the end.

11. Add a final "Review Notice" explaining that this is an
AI-generated draft and should be reviewed for the applicable jurisdiction.

12. Do not claim that the document is attorney-approved.

13. Return plain text only.

14. Do not use Markdown code blocks.

Generate the complete document now.
"""

        return prompt.strip()

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:

        prompt = self.build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        generated_text = getattr(response, "text", None)

        if not generated_text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return generated_text.strip()