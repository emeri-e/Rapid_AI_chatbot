import openai



openai.api_key = ''
#with open('models.json', 'w') as json_file:
#  json.dump(openai.Model.list(), json_file)


class Message:
    
    
    def __init__(self,role,content):
        
        self.role = role
        self.content = content

    def message(self):
        
        return {"role": self.role,"content": self.content}
        
# Our assistant class we'll use to converse with the bot
class Assistant:
    
    def __init__(self):
        self.conversation_history = []

    def _get_assistant_response(self, prompt):
        
        try:
            completion = openai.ChatCompletion.create(
              model="gpt-3.5-turbo",
              messages=prompt, max_tokens=2000
            )
            
            response_message = Message(completion['choices'][0]['message']['role'],completion['choices'][0]['message']['content'])
            return response_message.message()
            
        except Exception as e:
            
            return f'Request failed with exception {e}'

    def ask_assistant(self, next_user_prompt, colorize_assistant_replies=True):
        [self.conversation_history.append(x) for x in next_user_prompt]
        assistant_response = self._get_assistant_response(self.conversation_history)
        self.conversation_history.append(assistant_response)
        return assistant_response
            
        
   



