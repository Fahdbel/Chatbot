import numpy as np
import pandas as pd
import streamlit as st
import openai
import os

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load CSV file
file_path = "Recap_CA_tabule_VF.csv"
try:
    df = pd.read_csv(file_path, header=1)  # Start reading from the actual header row
    df.columns = df.columns.str.strip()  # Remove any extra spaces from column names
    st.write("Columns in the DataFrame:", df.columns)  # Debug: Print column names
except FileNotFoundError:
    st.error(f"Le fichier {file_path} n'a pas été trouvé.")
    st.stop()

# #### Base de connaissances avec réponses pré-définies
BASE_KNOWLEDGE = {
    "performances courtiers 2024": "Le chiffre d'affaires total des courtiers pour 2024 à fin septembre est de 712 025 181 MAD.",
    "evolution courtiers 2023 2024": "L'évolution du chiffre d'affaires des courtiers de 2023 à 2024 est de -31%.",
    "DAB courtiers 2024": "Le chiffre d'affaires du produit DAB pour les courtiers en 2024 est de 194 558 598 MAD.",
    "transport courtiers 2022": "Le chiffre d'affaires pour le produit Transport chez les courtiers en 2022 est de 62 055 611 MAD.",
    "evolution accidents 2021 2022": "La performance de l'assurance individuelle accidents des courtiers a augmenté de 16%, passant de 5 347 536 MAD en 2021 à 6 219 037 MAD en 2022.",
    # Add other predefined responses here
}

def get_predefined_response(question):
    """
    Function to match keywords with predefined responses.
    """
    question = question.lower()
    for keyword, response in BASE_KNOWLEDGE.items():
        if all(word in question for word in keyword.split()):
            return response
    return None

def ask_llm_with_data(question):
    # Determine which year or metric to filter based on the question
    if "2021" in question:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2021"]].head(5).to_dict()
        year = "2021"
    elif "2022" in question:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2022"]].head(5).to_dict()
        year = "2022"
    elif "2023" in question:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2023"]].head(5).to_dict()
        year = "2023"
    elif "2024" in question:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2024"]].head(5).to_dict()
        year = "2024"
    else:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2021", "DIM_2022", "DIM_2023", "DIM_2024"]].head(5).to_dict()
        year = "2021-2024"

    # Prompt creation with relevant data
    prompt = (
        f"Voici les données de vente par intermédiaire pour l'année {year} :\n"
        f"{filtered_data}\n"
        f"Répondez précisément à la question suivante en fonction de ces données : {question}"
    )

    # Query the LLM
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"An error occurred: {e}"

# Streamlit Interface
st.title("Chatbot d'Analyse de Données")
question = st.text_input("Posez une question :")

if question:
    try:
        response = ask_llm_with_data(question)
        st.write("Réponse du chatbot :", response)
    except Exception as e:
        st.write(f"An error occurred: {e}")

def route_question(question):
    """
    Routing function to check for predefined responses first.
    """
    predefined_response = get_predefined_response(question)
    if predefined_response:
        return predefined_response
    else:
        return ask_llm_with_data(question)

# Additional Streamlit Interface for hybrid chatbot
st.title("Chatbot Hybride pour la Direction Générale")
st.write("Posez vos questions sur les performances commerciales et les produits d'assurance")

# Input field for questions
question = st.text_input("Votre question:")

# Display the response
if question:
    response = route_question(question)
    st.write("Réponse du chatbot :")
    st.write(response)

# streamlit run chatbot.py
