from openai import OpenAI

import requests

class GPT4:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", max_tokens: int = 1024):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens

    def gpt_4o_mini(self, prompt: str, text_wrap: int = 100):
        """
        Invoke the GPT-4o-mini API with the given prompt, returns the response.

        Parameters:
        - prompt (str): The prompt to send to the GPT-4o-mini API.
        - text_wrap (int): Optional parameter for text wrapping (not implemented here).

        Returns:
        - str: The response from the GPT-4o-mini API.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            response_json = response.json()

            # Calculate costs if usage is provided
            if 'usage' in response_json:
                prompt_tokens = response_json['usage']['prompt_tokens']
                completion_tokens = response_json['usage']['completion_tokens']
                cost = 0.15 * (prompt_tokens / 1_000_000) + 0.60 * (completion_tokens / 1_000_000)
                print(f"gpt-4o-mini cost: $0.15/1M input tokens x {prompt_tokens} + $0.60/1M output tokens x {completion_tokens} = ${cost:.6f}")

            # Return the response content
            if 'choices' in response_json and response_json['choices']:
                return response_json['choices'][0]['message']['content']
            else:
                return "No valid response received from the API."

        except requests.exceptions.RequestException as e:
            return f"API request failed: {e}"
        
    def gpt_4o_strict_syntax(self, 
                             user_prompt:str, 
                             syntax_instructions: str, 
                             rag_background_info: list,):
        strict_syntax_example = f"""
        You are a layout automation assistant. Translate the following human prompt into strict syntax for analog layout design.
        Here are guidelines you must follow for Strict Syntax:
        {syntax_instructions}

        Additionally, here is background information that may help inform your strict syntax design:
        1) {rag_background_info[0]}
        2) {rag_background_info[1]}
        3) {rag_background_info[2]}

        Lastly, here are some examples of strict syntax:
        Example 1:
            Here is an example of strictsyntax:
                RegulatedCascode
                create a float parameter called cascode_width
                create a float parameter called feedback_width
                create a float parameter called cascode_length
                create a float parameter called feedback_length
                create a int parameter called cascode_multiplier
                create a int parameter called feedback_multiplier
                create a int parameter called cascode_fingers
                create a int parameter called feedback_fingers
                place a nmos called cascode with width=cascode_width, length=cascode_length, fingers=cascode_fingers, rmult=1, multipliers=cascode_multiplier, with_substrate_tap=False, with_tie=False, with_dummy=False 
                place a nmos called feedback with width=feedback_width, length=feedback_length, fingers=feedback_fingers, rmult=1, multipliers=feedback_multiplier, with_substrate_tap=False, with_tie=False, with_dummy=False 
                move feedback below cascode
                route between cascode_gate_E and feedback_drain_E using smart_route
                route between feedback_gate_W and feedback_source_W using smart_route

        Example 2:
            Human Prompt: {user_prompt}:
            Generate strict syntax for this layout.
        """

        response = self.gpt_4o_mini(strict_syntax_example)
        print(response)
        return response

    def gpt_4o_parameters(self, prompt, parameters):
        text = f"""
        I am {prompt}. You have been provided with a set of parameters for a Python function: {parameters}.
        Your task is to analyze the parameters and generate a Python list of dictionaries.

        Each dictionary should describe a parameter with the following structure:
        - `name`: (str) The name of the parameter.
        - `type`: (str) The type of the parameter, such as 'int', 'float', 'str', etc.
        - `default`: (any) The default value for the parameter, or `None` if no default is provided.
        - `value`: (any) A realistic or contextually appropriate value for the parameter.

        Example output for the parameters ['width', 'height']:
        [
            {{'name': 'width', 'type': 'float', 'default': None, 'value': 1.5}},
            {{'name': 'height', 'type': 'int', 'default': 0, 'value': 10}}
        ]

        Ensure the values make sense in the context of the parameter names. If a default is provided, use it as the value unless instructed otherwise.

        Only output the list of dictionaries as valid Python syntax. Do not include explanations or additional text.
        """
        response = self.gpt_4o_mini(text)
        return response
