import os
from google import genai
from pydantic import BaseModel, Field
from typing import Optional

from ..prompts import load_prompt, PROMPTS_DIR

class ErrorOutput(BaseModel):
    localizacao_ficheiro: str = Field(description="Ecoado da entrada.")
    erro: str = Field(description="Descrição do erro.")
    grupo_documento: Optional[str] = Field(default=None, description="O valor recebido no campo grupo_documento da entrada.")
    notas_triagem: Optional[str] = Field(default=None, description="Nota explicativa sobre a falha na triagem.")
    notas_classificacao: Optional[str] = Field(default=None, description="Nota explicativa sobre a falha na classificação.")

class BaseAgent:

    def __init__(self, response_type, prompt_name, model="gemini-2.5-flash-preview-05-20"):
        """Initialize the base agent.

        Args:
            response_type: Pydantic model for response validation
            prompt_name: Name of the prompt file (without .md extension)
            model: AI model to use for generation
        """
        self.client = genai.Client()
        self.model = model

        # Load prompt from the prompts package
        prompt_path = PROMPTS_DIR / f"{prompt_name}.md"
        self.prompt_ref = self.client.files.upload(file=str(prompt_path))
        self.response_type = response_type

    def _run(self, input_prefix, input, ):
        try:
            true_input = self.client.files.upload(file=input) if os.path.isfile(input) else input

            response = self.client.models.generate_content(
                model=self.model,
                contents=[self.prompt_ref,  input_prefix, true_input],

                config={
                    "response_mime_type": "application/json",
                    "response_schema": self.response_type
                })

            return response.parsed #type: ignore
        except Exception as e:
            print("Error processing prompt")

            return ErrorOutput(
                localizacao_ficheiro= "UNKNOWN",
                grupo_documento= "ERROR",
                erro= f"{e}"
            )
