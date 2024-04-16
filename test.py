from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()

try:
    # Open the add_games page
    driver.get("http://127.0.0.1:5000/add_games")  # Update with the actual URL

    # Find the input fields and submit button
    gender_field = driver.find_element(By.NAME, "gender")
    game_name_field = driver.find_element(By.NAME, "game_name")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

    # Test case: Add a new game successfully
    gender_field.send_keys("Male")  # Provide valid gender input
    game_name_field.send_keys("Football")  # Provide a new game name
    submit_button.click()

    # Wait for the success message
    success_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))
    )
    assert "Game added successfully!" in success_message.text
    print("Test passed: Game added successfully!")

    # Test case: Attempt to add an existing game
    gender_field.clear()  # Clear the input fields
    game_name_field.clear()
    gender_field.send_keys("Female")  # Provide valid gender input
    game_name_field.send_keys("Football")  # Provide an existing game name
    submit_button.click()

    # Wait for the error message
    error_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "alert-error"))
    )
    assert "The game already exists." in error_message.text
    print("Test passed: Game already exists error message displayed.")

except Exception as e:
    print("Test failed:", e)

finally:
    # Close the browser window
    driver.quit()
