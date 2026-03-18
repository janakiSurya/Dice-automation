# src/ai_helper.py

import yaml
import os
import logging
import time
import json
import requests

# Configure logging for ai_helper.py
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("application.log"),
        logging.StreamHandler(),
    ],
)


def load_config(config_path="src/config.yaml"):
    """
    Load configuration from a YAML file.

    :param config_path: Path to the config.yaml file.
    :return: Configuration dictionary.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.info("Configuration loaded successfully.")
        logging.debug(f"Configuration content: {config}")  # Added for debugging
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file {config_path} not found.")
        return {}
    except yaml.YAMLError as exc:
        logging.error(f"Error parsing {config_path}: {exc}")
        return {}

def initialize_openai(config):
    """
    Initialize the Google Gemini configuration by validating that the API key is present.

    :param config: Configuration dictionary (unused, kept for backward compatibility).
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error(
                "GEMINI_API_KEY environment variable is not set. "
                "Set it before running the application."
            )
            raise KeyError("Missing GEMINI_API_KEY in environment.")

        # Simple log so we fail early if the key is missing; no client object is required.
        logging.info("Gemini API key detected in environment.")
    except KeyError as e:
        logging.error(f"KeyError during Gemini initialization: {e}")
    except Exception as e:
        logging.error(f"Error during Gemini initialization: {e}")

def load_data(data_path="src/data.yaml"):
    """
    Load personal data from a YAML file.

    :param data_path: Path to the data.yaml file.
    :return: Personal data dictionary.
    """
    try:
        with open(data_path, 'r') as file:
            data = yaml.safe_load(file)
        logging.info("Personal data loaded successfully from data.yaml.")
        logging.debug(f"Personal data content: {data}")  # Added for debugging
        return data
    except FileNotFoundError:
        # If the real profile file isn't present (for example in a fresh public repo),
        # fall back to the example so the program can still start.
        fallback_path = data_path.replace("data.yaml", "data.example.yaml")
        logging.warning(f"Data file {data_path} not found. Trying fallback: {fallback_path}")
        try:
            with open(fallback_path, 'r') as file:
                data = yaml.safe_load(file)
            logging.info(f"Personal data loaded successfully from {fallback_path}.")
            logging.debug(f"Personal data content: {data}")  # Added for debugging
            return data
        except FileNotFoundError:
            logging.error(f"Fallback data file {fallback_path} not found.")
            return {}
    except yaml.YAMLError as exc:
        logging.error(f"Error parsing {data_path}: {exc}")
        return {}

def get_openai_response(question, data, options=None, retries=3, delay=5):
    """
    Generate a response for a given question using Google's Gemini API and the provided data.
    Handles both textual answers and selection-based answers like radio buttons.

    :param question: The question extracted from the form's label.
    :param data: The parsed YAML data as a dictionary.
    :param options: The list of radio button options (if applicable).
    :param retries: Number of retry attempts.
    :param delay: Delay between retries in seconds.
    :return: The generated response string (text answer or selected option).
    """
    data_json = json.dumps(data, indent=2)

    # If options are provided, include them in the prompt for the model
    if options:
        options_text = "\n".join([f"- {option}" for option in options])
        prompt = f"""
You are an assistant that helps fill out job application forms based on the user's personal data.

Personal data:
{data_json}

Question:
"{question}"

Here are the possible options:
{options_text}

Choose the most appropriate option based on the user's personal data and return only the chosen option.
"""
    else:
        prompt = f"""
You are an assistant that helps fill out job application forms based on the user's personal data.

Personal data:
{data_json}

Question:
"{question}"

Provide a concise and appropriate answer based on the personal data.
"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error(
            "GEMINI_API_KEY environment variable is not set. "
            "Set it before running the application."
        )
        return "NA"

    model = "gemini-2.5-flash"
    url = (
        f"https://generativelanguage.googleapis.com/v1/models/"
        f"{model}:generateContent?key={api_key}"
    )

    for attempt in range(1, retries + 1):
        try:
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt,
                            }
                        ]
                    }
                ],
            }
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Gemini API error {response.status_code}: {response.text}"
                )

            data_resp = response.json()
            candidates = data_resp.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from Gemini.")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise ValueError("No content parts returned from Gemini.")

            answer = (parts[0].get("text") or "").strip()
            if not answer:
                raise ValueError("Empty response text from Gemini.")

            logging.info(f"Generated response for question '{question}': {answer}")
            return answer
        except Exception as e:
            logging.error(
                f"Attempt {attempt} - Error generating response from Gemini: {e}"
            )
            if attempt < retries:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error("All retry attempts failed. Using 'NA' as fallback.")
                return "NA"