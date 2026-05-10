import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please create a .env file with your API key.")

client = genai.Client(api_key=api_key)

try:
    with open('emissions.json', 'r', encoding='utf-8') as f:
        content = f.read()

except FileNotFoundError:
    print("Error: The file 'file.txt' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")


response = client.models.generate_content(
    model="gemini-2.5-flash", contents="I will give the carbon emissions data which we predicted for our campus. Give me perfect insights clearly in 10 lines. "+content
)
print(response.text)





