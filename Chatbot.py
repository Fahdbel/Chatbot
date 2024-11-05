import numpy as np
import pandas as pd
import streamlit as st
import openai


openai.api_key = "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"



# #### Base de connaissances avec réponses pré-définies

BASE_KNOWLEDGE = {
    "performances courtiers 2024": "Le chiffre d'affaires total des courtiers pour 2024 à fin septembre est de 712 025 181 MAD.",
    "evolution courtiers 2023 2024": "L'évolution du chiffre d'affaires des courtiers de 2023 à 2024 est de -31%.",
    "DAB courtiers 2024": "Le chiffre d'affaires du produit DAB pour les courtiers en 2024 est de 194 558 598 MAD.",
    "transport courtiers 2022": "Le chiffre d'affaires pour le produit Transport chez les courtiers en 2022 est de 62 055 611 MAD.",
    "evolution accidents 2021 2022": "La performance de l'assurance individuelle accidents des courtiers a augmenté de 16%, passant de 5 347 536 MAD en 2021 à 6 219 037 MAD en 2022.",
    # Ajoutez d'autres réponses ici en suivant le même format
}


def get_predefined_response(question):
    """
    Fonction qui utilise la correspondance par mots-clés pour trouver la réponse pré-définie.
    """
    question = question.lower()
    for keyword, response in BASE_KNOWLEDGE.items():
        if all(word in question for word in keyword.split()):
            return response
    return None


def ask_llm(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can also use "gpt-4" if available in your API key's access
            messages=[{"role": "user", "content": question}],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error occurred: {e}")
        return "An error occurred while fetching the response."


def route_question(question):
    """
    Fonction de routage qui vérifie d'abord les réponses pré-définies, puis envoie au LLM si nécessaire.
    """
    predefined_response = get_predefined_response(question)
    if predefined_response:
        return predefined_response
    else:
        return ask_llm(question)


# #### Interface utilisateur avec Streamlit


st.title("Chatbot Hybride pour la Direction Générale")
st.write("Posez vos questions sur les performances commerciales et les produits d'assurance")

# Champ de texte pour poser la question
question = st.text_input("Votre question:")

# Afficher la réponse si une question est posée
if question:
    response = route_question(question)
    st.write("Réponse du chatbot :")
    st.write(response)


# streamlit run chatbot.py

