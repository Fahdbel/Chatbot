import numpy as np
import pandas as pd
import streamlit as st
import openai
import os

# Configurez la clé API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Chargement du fichier CSV avec un délimiteur spécifique
file_path = "Recap_CA_tabule_VF.csv"
try:
    df = pd.read_csv(file_path, header=1, delimiter=';', index_col = 0)  # Ajouter delimiter=';' si le fichier utilise des points-virgules
    df.columns = df.columns.str.strip()  # Supprime les espaces autour des noms de colonnes
#    st.write("Colonnes du DataFrame:", df.columns)  # Affiche les colonnes pour vérification
except FileNotFoundError:
    st.error(f"Le fichier {file_path} n'a pas été trouvé.")
    st.stop()


# Base de connaissances pour les réponses pré-définies
BASE_KNOWLEDGE = {
    "performances courtiers 2024": "Le chiffre d'affaires total des courtiers pour 2024 à fin septembre est de 712 025 181 MAD.",
    "evolution courtiers 2023 2024": "L'évolution du chiffre d'affaires des courtiers de 2023 à 2024 est de -31%.",
    "DAB courtiers 2024": "Le chiffre d'affaires du produit DAB pour les courtiers en 2024 est de 194 558 598 MAD.",
    "transport courtiers 2022": "Le chiffre d'affaires pour le produit Transport chez les courtiers en 2022 est de 62 055 611 MAD.",
    "evolution accidents 2021 2022": "La performance de l'assurance individuelle accidents des courtiers a augmenté de 16%, passant de 5 347 536 MAD en 2021 à 6 219 037 MAD en 2022.",
    # Ajoutez d'autres réponses ici si nécessaire
}

def get_predefined_response(question):
    """
    Cherche une réponse pré-définie basée sur les mots-clés de la question.
    """
    question = question.lower()
    for keyword, response in BASE_KNOWLEDGE.items():
        if all(word in question for word in keyword.split()):
            return response
    return None

def ask_llm_with_data(question):
    # Analyse basique de la question pour identifier l'année ou la métrique concernée
    if "2021" in question:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2021"]].head(100).to_dict()
    elif "2022" in question:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2022"]].head(100).to_dict()
    elif "2023" in question:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2023"]].head(100).to_dict()
    elif "2024" in question:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2024"]].head(100).to_dict()
    else:
        filtered_data = df[["TYPE_INTERMEDIAIRE", "DIM_2021", "DIM_2022", "DIM_2023", "DIM_2024"]].head(100).to_dict()

    # Créer le prompt
    prompt = (
        f"Voici les données de vente par intermédiaire pour l'année concernée :\n"
        f"{filtered_data}\n"
        f"Répondez précisément à la question suivante en fonction de ces données : {question}"
    )

    # Interroger le LLM avec les données
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

def route_question(question):
    """
    Fonction de routage qui vérifie d'abord les réponses pré-définies, puis interroge le LLM si nécessaire.
    """
    predefined_response = get_predefined_response(question)
    if predefined_response:
        return predefined_response
    else:
        return ask_llm_with_data(question)

# Interface utilisateur unique
st.title("Chatbot pour la Direction Générale")
st.write("Posez vos questions sur les performances commerciales et les produits d'assurance")

# Champ de texte pour poser la question
question = st.text_input("Votre question :")

# Afficher la réponse si une question est posée
if question:
    response = route_question(question)
    st.write("Réponse du chatbot :")
    st.write(response)
