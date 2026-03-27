# src/app.py

from login import login_to_dice
from job_search import search_jobs, apply_to_jobs
from ai_helper import load_config, initialize_openai, load_data
from selenium import webdriver
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import logging


def main():
    load_dotenv()

    config = load_config()
    logging.debug(f"Loaded config: {config}")

    initialize_openai(config)

    data = load_data()
    logging.debug(f"Loaded data: {data}")

    options = webdriver.ChromeOptions()

    # Local -> visible browser
    # GitHub Actions -> headless browser
    if os.getenv("CI", "false").lower() == "true":
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        username = os.getenv("DICE_USERNAME", config.get("credentials", {}).get("username"))
        password = os.getenv("DICE_PASSWORD", config.get("credentials", {}).get("password"))

        if not username or not password:
            logging.error("Dice credentials not found. Set DICE_USERNAME and DICE_PASSWORD in .env.")
            return

        login_to_dice(driver, username, password)

        days_posted = config.get("search_params", {}).get("days_posted", 1)
        search_jobs(
            driver,
            config["search_params"]["keyword"],
            config["search_params"]["location"],
            days_posted,
        )
        apply_to_jobs(driver, data)

    finally:
        driver.quit()
        logging.info("WebDriver closed.")


if __name__ == "__main__":
    main()