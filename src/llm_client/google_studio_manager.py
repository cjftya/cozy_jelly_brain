
from typing import Any

from google import genai
from google.genai import types

from llm_client.base_client import BaseClient
from llm_client.cognitive_schema import OrganicCognitiveResponse


class GoogleStudioManager(BaseClient):
    def __init__(self):
        self._api_key = None
        self.__model_name = "gemini-3.1-flash-lite"
        self.client = None

    def set_api_key(self, api_key):
        self._api_key = api_key
        if self._api_key:
            self.client = genai.Client(api_key=self._api_key)

    def get_options(self):
        return {"temperature": 0.6, "top_p": 0.9, "top_k": 40}

    def get_installed_models(self):
        return ["gemini-3.1-flash-lite"]

    def set_model_name(self, model_name):
        self.__model_name = model_name

    def get_context_size(self):
        return 1048576

    def request(self, context, model=None, options=None, chunk_callback=None):
        if not self.client and self._api_key:
            self.client = genai.Client(api_key=self._api_key)

        if not self.client:
            return {
                "message": {
                    "content": "Error: API Key is not set or client initialization failed."
                },
                "prompt_eval_count": 0,
                "eval_count": 0,
            }

        target_model = model if model else self.__model_name

        system_instruction = None
        contents: Any = []

        if isinstance(context, list):
            for msg in context:
                role = msg.get("role")
                text = msg.get("content") or ""
                if role == "system":
                    system_instruction = text
                else:
                    contents.append(
                        types.Content(
                            role="model" if role == "assistant" else "user",
                            parts=[types.Part.from_text(text=text)],
                        )
                    )
        else:
            contents = [
                types.Content(
                    role="user", parts=[types.Part.from_text(text=context or "")]
                )
            ]

        op = options.copy() if options else self.get_options()

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=op.get("temperature"),
                top_p=op.get("top_p"),
                top_k=op.get("top_k"),
                response_mime_type="application/json",
                response_schema=OrganicCognitiveResponse,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MEDIUM
                ),
            )

            response_stream = self.client.models.generate_content_stream(
                model=target_model, contents=contents, config=config
            )

            full_response: dict[str, Any] = {"message": {"content": ""}}
            for chunk in response_stream:
                if chunk.text:
                    full_response["message"]["content"] += chunk.text
                    if chunk_callback:
                        chunk_callback(chunk.text)

            usage = getattr(response_stream, "usage_metadata", None)
            full_response.update(
                {
                    "prompt_eval_count": getattr(usage, "prompt_token_count", 0),
                    "eval_count": getattr(usage, "candidates_token_count", 0),
                }
            )

            return full_response

        except Exception as e:
            return {
                "message": {"content": f"Error: {str(e)}"},
                "prompt_eval_count": 0,
                "eval_count": 0,
            }
