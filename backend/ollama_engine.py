import ollama


class OllamaEngine:
    def __init__(self):
        pass

    def set_model(self, model:str): 
        self.model = model
        # add check if the model exists

    def check_models(self, user_model_folder = False):
        downloaded_ollama_models = None
        pass # complete checks for models in ollama and user folder

    def process_prompt(self, user_prompt:str, system_prompt:str):
         full_prompt = system_prompt + user_prompt
         resp = ollama.chat(
                    model=self.model,
                    keep_alive=600,
                    messages=[{
                        "role": "user",
                        "content": full_prompt
                    }]
         )
         return resp["message"]["content"]
