from openai import OpenAI

import requests

class GPT4:
    """
    A wrapper class for interacting with the GPT-4o-mini API.
    """
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
                             rag_background_info: list,
                             convo_background_info: list):
        """
        Generates strict syntax for layout design based on the user's prompt.

        Args:
            user_prompt (str): The user's prompt describing the layout task.
            syntax_instructions (str): Guidelines for translating the prompt into strict syntax.
            rag_background_info (list): A list of relevant background information from retrieval-augmented generation (RAG).
            convo_background_info (list): A list of example strict syntax conversations for additional context, also from RAG.

        Returns:
            str: The strict syntax generated by the GPT-4o-mini model.
        """

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
            {convo_background_info[0]}
        Example 2:
            {convo_background_info[1]}
        Example 3:
            {convo_background_info[2]}
            
        Human Prompt: {user_prompt}:
            Generate strict syntax for this human prompt.
            Do not generate comments, only strict syntax.
        """
        response = self.gpt_4o_mini(strict_syntax_example)
        return response

    def gpt_4o_parameters(self, prompt, parameters, feedback=""):
        """
        Generates a list of dictionaries describing function parameters using GPT-4.
        """
        text = f"""
        I am {prompt}. You have been provided with a set of parameters for a Python function: {parameters}.
        {feedback}
        Your task is to analyze the parameters, stay within sky130 pdk parameters, and generate a Python list of dictionaries.

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

        Only output the list of dictionaries. Do not include any other syntax or words.
        """
        response = self.gpt_4o_mini(text)
        return response

    def gpt_4o_comp_feedback(self, 
                                user_prompt:str, 
                                syntax_instructions: str, 
                                rag_background_info: list,
                                convo_background_info: list,
                                close_comp_suggestion,
                                close_comp_dependencies,
                                all_legal_imports):
        """
        Generates strict syntax for layout design using GPT-4o-mini, based on the user's prompt.

        This function processes a human-readable prompt and translates it into strict syntax 
        for analog layout design. The translation adheres to specified syntax guidelines and 
        incorporates contextual background information and import suggestions.

        Args:
            user_prompt (str): The user's natural language description of the layout task.
            syntax_instructions (str): Guidelines or rules to ensure adherence to strict syntax formatting.
            rag_background_info (list): Background information from retrieval-augmented generation (RAG) 
                                        to provide additional context for the layout task. Expected to 
                                        contain up to three relevant pieces of information.
            convo_background_info (list): Examples of strict syntax from prior conversations to guide 
                                        the model. Expected to contain up to three examples.
            close_comp_suggestion (str): A single close-matching component suggested as potentially 
                                        useful based on the user's prompt.
            close_comp_dependencies (list): A list of related components that the close-matching 
                                            component depends on, if applicable.
            all_legal_imports (list): A complete list of valid imports available for use in the strict 
                                    syntax generation, ensuring compliance with the knowledge graph.

        Returns:
            str: Strict syntax generated by GPT-4o-mini, based on the user's input and contextual information.

        Notes:
            - The strict syntax generated avoids using imports unless they are explicitly validated
            or included in the provided legal imports list.
            - The function prioritizes correctness by providing relevant component suggestions and 
            dependencies while adhering to strict syntax rules.
            - Comments are excluded from the output to maintain syntax purity.
        """

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
            {convo_background_info[0]}
        Example 2:
            {convo_background_info[1]}
        Example 3:
            {convo_background_info[2]}
            
        Human Prompt: {user_prompt}:
            Generate strict syntax for this human prompt. Avoid using imports unless you are 100% confident they exist within GLayout.
            Do not generate comments, only strict syntax.

            Additionally, here are some possible imports you may use for this design. You do not have to use it but do not make up any imports.
            Possibly useful import: {close_comp_suggestion}
            Possibly related useful imports: {close_comp_dependencies}
            All legal imports: {all_legal_imports}
        """
        response = self.gpt_4o_mini(strict_syntax_example)
        return response
