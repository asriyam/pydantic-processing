from pydantic import BaseModel, ValidationError, EmailStr, Field
from typing import List, Literal, Optional
from dotenv import load_dotenv
import openai
import json
import datetime
import openai

load_dotenv()

client = openai.OpenAI()

class UserInput(BaseModel):
    name: str
    email: EmailStr
    query: str
    order_id: Optional[int] = Field(None, description="5 digit order number (cannot start with 0)", ge=10000, le=99999)

user_input_json = '''
{
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I forgot my password. Urgently need access, help!!!",
    "order_number": null,
    "purchase_date": null
}
'''

user_input = UserInput.model_validate_json(user_input_json)

class CustomerQuery(UserInput):
    priority: str = Field(..., description="Priority level: low, medium, high")
    category: Literal['refund_request', 'information_request', 'other'] = Field(..., description="Query category")
    is_complaint: bool = Field(..., description='Whether this is a complaint')
    tags: List[str] = Field(..., description="Relevant keyword tags")

example_response_structure = f"""{{
    name="Example User",
    email="user@example.com",
    query="I ordered a new computer monitor and it arrived with the screen cracked. I need to exchange it for a new one.",
    order_id=12345,
    purchase_date="2025-12-31",
    priority="medium",
    category="refund_request",
    is_complaint=True,
    tags=["monitor", "support", "exchange"] 
}}"""

prompt = f"""Please analyze this query \n {user_input.model_dump_json(indent=2)}:  
    Return your analysis as a JSON object matching this exact structure and data types:
    {example_response_structure}

   Respond ONLY with valid JSON. Do not include any explanations or other text or formatting before or after the JSON object.
"""
#print(prompt)

def call_llm(prompt, model="gpt-4o"):   
    response = client.chat.completions.create(
        model=model,
        messages=[{"role":"user", "content": prompt}]
    )
    return response.choices[0].message.content

response_content = call_llm(prompt)
print(response_content)

"""
user_input = UserInput(
    name = "Joe str",
    email = "joe@dell.com",
    query = "I forgot my password.",
    order_id=None
)

def validate_user_input(input_data):
    try:
        user_input = UserInput(**input_data)        
        print(f"Valid user input data {user_input.model_dump_json(indent=2)}")
    except ValidationError as e:
        print("Validation error occurred")
        for error in e.errors():
            print(f" - {error['loc'][0]}: {error['msg']}")
    return None

validate_user_input(input_data={
    "name": "Bell",
    "email": "bell@dell.com", 
    "query": "I forgot my password"
})
"""