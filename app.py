import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

# Read API key
# with open("key.txt") as f:
#     OPENAI_API_KEY = f.read().strip()
OPENAI_API_KEY = "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"

# Define output structure
class RecipeOutput(BaseModel):
    ingredients: List[str] = Field(..., description="List of ingredients with amount, in English (Hindi)")
    instructions: List[str] = Field(..., description="Step-by-step instructions to cook the dish")


recipe_output_parser = PydanticOutputParser(pydantic_object=RecipeOutput)

# Set up LangChain model
chat_model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")

# Prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     """You are a helpful AI chef assistant. Given a dish name by the user, provide:
     1. A list of ingredients in the format: english (hindi)
     2. A numbered list of step-by-step cooking instructions with amount of the ingredients.

     {format_instructions}"""
     ),
    ("human", "Give me the recipe for {dish_name}."),
])

# Chain
chain = prompt_template | chat_model | recipe_output_parser

# Streamlit UI
st.set_page_config(page_title="AI Recipe Assistant", page_icon="🍽️")
st.title("🍽️ AI Recipe Generator")

dish_name = st.text_input("Enter the name of a dish:", placeholder="e.g., Paneer Biryani")

if st.button("Generate Recipe") and dish_name:
    with st.spinner("Cooking up your recipe..."):
        user_input = {
            "dish_name": dish_name,
            "format_instructions": recipe_output_parser.get_format_instructions()
        }
        try:
            response = chain.invoke(user_input)

            st.subheader("📝 Ingredients")
            for ing in response.ingredients:
                st.markdown(f"- {ing}")

            st.subheader("👨‍🍳 Instructions")
            for i, step in enumerate(response.instructions, 1):
                st.markdown(f"{i}. {step}")

        except Exception as e:
            st.error(f"Error: {e}")
