from google import genai
from google.genai import types
from llm_client.base_client import BaseClient

class GoogleStudioManager(BaseClient):
    def __init__(self):
        self._api_key = None
        self.__model_name = "gemini-3.1-flash-lite-preview"

    def set_api_key(self, api_key):
        self._api_key = api_key

    def get_options(self):
        return {
            "temperature": 0.8,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }

    def get_installed_models(self):
        return ["gemini-3.1-flash-lite-preview"]

    def set_model_name(self, model_name):
        self.__model_name = model_name

    def get_context_size(self):
        return 1048576

    def request(self, context, model=None, options=None, chunk_callback=None):
        client = genai.Client(api_key=self._api_key)
        target_model = model if model else self.__model_name

        system_instruction = None
        contents = []

        if isinstance(context, list):
            for msg in context:
                role = msg.get("role")
                text = msg.get("content") or ""
                if role == "system":
                    system_instruction = text
                else:
                    # 'assistant' 역할을 'model'로 정확히 매핑
                    contents.append({
                        "role": "model" if role == "assistant" else "user",
                        "parts": [{"text": text}]
                    })
        else:
            contents = [{"role": "user", "parts": [{"text": context or ""}]}]

        op = options.copy() if options else self.get_options()
        
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=op.get("temperature"),
                max_output_tokens=op.get("max_output_tokens"),
                top_p=op.get("top_p"),
                top_k=op.get("top_k"),
                response_mime_type="application/json"
            )

            response_stream = client.models.generate_content_stream(
                model=target_model,
                contents=contents,
                config=config
            )

            full_response = {"message": {"content": ""}}
            for chunk in response_stream:
                if chunk.text:
                    full_response["message"]["content"] += chunk.text
                    if chunk_callback:
                        chunk_callback(chunk.text)
            
            usage = getattr(response_stream, 'usage_metadata', None)
            full_response.update({
                "prompt_eval_count": getattr(usage, 'prompt_token_count', 0),
                "eval_count": getattr(usage, 'candidates_token_count', 0)
            })

            return full_response
            
        except Exception as e:
            return {"message": {"content": f"Error: {str(e)}"}, "prompt_eval_count": 0, "eval_count": 0}