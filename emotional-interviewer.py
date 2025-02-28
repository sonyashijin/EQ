import os
import sys
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Global debug flag
DEBUG = True

class Interviewer:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.system_prompt = (
            "You are an interviewer conducting a job assessment interview on a candidate's Product management skills. "
            "Please focus on the following areas of interest: "
            "(a) market positioning of the new product, "
            "(b) competitive analysis, "
            "(c) TAM calculation, "
            "(d) MRD and PRD creation, "
            "(e) engineering, "
            "(f) pre-launch and launch, "
            "(g) maintenance and EOL cycles. "
            "Make it general enough to test the candidate's knowledge and ask them to provide specific examples."
            "Keep the interview conversational and engaging and to the point. When all areas are covered, ask the candidate if they have any questions."
            "Do not output bullet points, markdown titles, or other formatting. Just output the text in a clear and easy to read format."
        )
        self.conversation_history = []

    def call_anthropic_api(self, messages):
        # Debug: Print accumulated context before API call
        if DEBUG:
            print("\n----- DEBUG: CONTEXT BEING SENT TO API -----")
            print("Messages:")
            for msg in messages:
                print(f"  {msg['role']}: {msg['content'][:100]}..." if len(msg['content']) > 100 else f"  {msg['role']}: {msg['content']}")
            print("---------------------------------------------\n")
        
        client = Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            system=self.system_prompt,
            messages=messages
        )
        return message.content[0].text

    def conduct_interview(self, opening_message=None):
        messages = []
        user_input = ""
        
        # If an opening message is provided, use it to start the conversation
        if opening_message:
            print("Candidate:", opening_message)
            self.conversation_history.append({"role": "user", "content": opening_message})
            messages.append({"role": "user", "content": opening_message})
            
            interviewer_response = self.call_anthropic_api(messages)
            print("Interviewer:", interviewer_response)
            
            self.conversation_history.append({"role": "assistant", "content": interviewer_response})
            messages.append({"role": "assistant", "content": interviewer_response})
        # Otherwise, start with an initial message from the assistant
        elif not self.conversation_history:
            initial_message = self.call_anthropic_api([])
            print("Interviewer:", initial_message)
            self.conversation_history.append({"role": "assistant", "content": initial_message})
            messages.append({"role": "assistant", "content": initial_message})
        
        while user_input.lower() != "exit":
            user_input = input("Candidate: ")
            if user_input.lower() == "exit":
                break
                
            self.conversation_history.append({"role": "user", "content": user_input})
            messages.append({"role": "user", "content": user_input})
            
            interviewer_response = self.call_anthropic_api(messages)
            print("Interviewer:", interviewer_response)
            
            self.conversation_history.append({"role": "assistant", "content": interviewer_response})
            messages.append({"role": "assistant", "content": interviewer_response})

    def main(self):
        print("Welcome to the Product Management Interview!")
        
        # Check if an opening message was provided as a command-line argument
        opening_message = None
        if len(sys.argv) > 1:
            opening_message = " ".join(sys.argv[1:])
        
        self.conduct_interview(opening_message)

if __name__ == "__main__":
    # Check for debug flag in environment
    if os.getenv("DEBUG", "").lower() in ("true", "1", "yes"):
        DEBUG = True
        print("Debug mode enabled")
    
    interviewer = Interviewer()
    interviewer.main()

