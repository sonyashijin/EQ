import os
import sys
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Global debug flag
DEBUG = False

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
        self.messages = []

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

    def get_response(self, user_input):
        """Function mode: Get a single response from the interviewer"""
        # Initialize conversation if this is the first interaction
        if not self.conversation_history:
            if user_input:
                # If user provided an opening message, use it
                self.conversation_history.append({"role": "user", "content": user_input})
                self.messages.append({"role": "user", "content": user_input})
                interviewer_response = self.call_anthropic_api(self.messages)
            else:
                # Otherwise start with an assistant message
                initial_message = self.call_anthropic_api([{"role": "user", "content": "Hello, I'm here for the interview."}])
                self.conversation_history.append({"role": "assistant", "content": initial_message})
                self.messages.append({"role": "assistant", "content": initial_message})
                return initial_message
        else:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.messages.append({"role": "user", "content": user_input})
        
        # Get response from API
        interviewer_response = self.call_anthropic_api(self.messages)
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": interviewer_response})
        self.messages.append({"role": "assistant", "content": interviewer_response})
        
        return interviewer_response

    def conduct_interview(self, opening_message=None, function_mode=False):
        """
        Conduct the interview either in CLI mode or function mode
        
        Args:
            opening_message: Optional initial message from the candidate
            function_mode: If True, just process the opening message and return
                          If False, run in interactive CLI mode
        """
        # Function mode - just process one message and return
        if function_mode:
            return self.get_response(opening_message)
        
        # CLI mode - interactive session
        user_input = ""
        
        # If an opening message is provided, use it to start the conversation
        if opening_message:
            print("Candidate:", opening_message)
            interviewer_response = self.get_response(opening_message)
            print("Interviewer:", interviewer_response)
        # Otherwise, start with an initial message from the assistant
        elif not self.conversation_history:
            initial_message = self.get_response(None)
            print("Interviewer:", initial_message)
        
        while user_input.lower() != "exit":
            user_input = input("Candidate: ")
            if user_input.lower() == "exit":
                break
                
            interviewer_response = self.get_response(user_input)
            print("Interviewer:", interviewer_response)

    def main(self):
        print("Welcome to the Product Management Interview!")
        
        # Check if we're in test function mode
        if len(sys.argv) > 1 and sys.argv[1] == "--test-function-mode":
            # Test the function mode with a series of messages
            test_messages = [
                "Hello, I'm here for the product management interview",
                "I have experience with market positioning through competitive analysis",
                "For TAM calculation, I typically start with the total market size",
                "exit"
            ]
            
            print("=== TESTING FUNCTION MODE ===")
            for msg in test_messages:
                if msg.lower() == "exit":
                    break
                print("Candidate:", msg)
                response = self.conduct_interview(msg, function_mode=True)
                print("Interviewer:", response)
            return
        
        # Regular CLI mode
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

