from openai import OpenAI
import os

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],
)

def openai_chat(prompt, messages):
    # Create an array of message objects
    message_array = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
    for role, content in messages:
        message_array.append({'role': role, 'content': content})

    # Generate a response from OpenAI
    response = OpenAI.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        messages=message_array,
        max_tokens=50  # Adjust the response length as per your requirement
    )

    # Retrieve the reply from OpenAI
    reply = response['choices'][0]['message']['content']

    return reply

# Example usage
prompt = "Who won the World Series in 2020?"

# Initial conversation messages
messages = [('user', 'Who won the World Series in 2020?')]

# Call the chat function
response = openai_chat(prompt, messages)

# Print the response
print(response)
