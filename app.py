# app.py

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import os

# Streamlit UI
st.title("🍛 AI Recipe Generator")
dish_name = st.text_input("Enter the dish name (e.g., mango juice):")

# Get API key from Streamlit secrets or text input
api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else st.text_input("Enter your OpenAI API key:", type="password")

if dish_name and api_key:
    # Define structured output format
    class RecipeOutput(BaseModel):
        ingredients: List[str] = Field(..., description="List of ingredients with amount of the ingredient, with English and Hindi")
        instructions: List[str] = Field(..., description="Step-by-step instructions to cook the dish")

    recipe_output_parser = PydanticOutputParser(pydantic_object=RecipeOutput)

    # Model
    chat_model = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")

    # Prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", 
         """You are a helpful AI chef assistant. Given a dish name by the user, provide:
         1. A list of ingredients in the format: english (hindi)
         2. A numbered list of step-by-step cooking instructions with amount of the ingredients.
         
         {format_instructions}"""
        ),
        ("human", "Give me the recipe for {dish_name}."),
    ])

    chain = prompt_template | chat_model | recipe_output_parser

    user_input = {
        "dish_name": dish_name,
        "format_instructions": recipe_output_parser.get_format_instructions()
    }

    with st.spinner("Generating recipe..."):
        try:
            response = chain.invoke(user_input)

            st.subheader("🍽️ Ingredients")
            for item in response.ingredients:
                st.markdown(f"- {item}")

            st.subheader("👨‍🍳 Instructions")
            for i, step in enumerate(response.instructions, 1):
                st.markdown(f"{i}. {step}")

        except Exception as e:
            st.error(f"Error: {e}")
