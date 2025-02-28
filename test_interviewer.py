from emotional_interviewer import Interviewer

def main():
    print("Testing the Interviewer class in function mode")
    print("---------------------------------------------")
    
    # List of candidate replies - easy to add new ones
    candidate_replies = [
        "Hello, I'm here for the interview",
        "I have experience with product management",
        "For market positioning, I typically analyze competitors and identify gaps",
        "When calculating TAM, I start with the total market size and narrow down"
    ]
    
    # Create an instance of the Interviewer
    interviewer = Interviewer()
    
    # Process all replies in a loop
    for reply in candidate_replies:
        print(f"\nCandidate: {reply}")
        response = interviewer.conduct_interview(reply, function_mode=True)
        print(f"Interviewer: {response}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main() 

