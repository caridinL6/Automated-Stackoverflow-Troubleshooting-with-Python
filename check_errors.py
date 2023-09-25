##################################################################################################################################################################################
##################################################################################################################################################################################
##################################################################################################################################################################################
##################################################################################################################################################################################
################################################# A simple Python script that checks the error message you're receiving from another script ######################################
#################################################      and queries Stack Overflow for the top 5 related messages and opens them for you     ######################################      
#################################################                                      by caridinl6                                         ######################################
##################################################################################################################################################################################
##################################################################################################################################################################################
##################################################################################################################################################################################

import subprocess
import requests
import json
import urllib.parse
import webbrowser
import logging

def main():
    
    # Collects user input with full path to their python script for running and troubleshooting. Input validation is incorporated into this part
    user_input = input("Provide full path to Python script giving you trouble: \n")
    program = ["python3", user_input]
    logging.info(f"[*] Try to run Python file at: {program}")

    if not validate_path(user_input):
        print("[*] Invalid path provided.")
        logging.error("[*] Invalid path provided.")
        return

    process = subprocess.Popen(program, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    output, error = process.communicate()
    if process.returncode == 0:
        print("[*] Command was successful.")
        #print("Output:")
        #print(output.decode('utf-8'))
    else:
        print("[*] Python file failed to run.")
        decoded_error = error.decode('utf-8')
        print(f"[*] Complete Error message: \n <<<<<<<<<<<<<<<START_OF_ERROR_MESSAGE>>>>>>>>>>>>>>>>>>> \n {decoded_error} \n <<<<<<<<<<<<<<<END_OF_ERROR_MESSAGE>>>>>>>>>>>>>>>\n")
        error_message = parse_error(decoded_error)  # Pass the decoded error message to the function

    if error_message:
        query_api(error_message)

# Handles user input gracefully.
def validate_path(path):
    try:
        with open(path, 'r') as file:
            return True
    except FileNotFoundError:
        return False

# Function processes error message and normalizes it for passing to the API
def parse_error(error_message):
    extracted_messages = []
    for line in error_message.splitlines():
        # Look for lines containing "error"
        if "error" in line.lower():
            extracted_message = line.strip()  # Keep "error:" prefix
            extracted_messages.append(extracted_message)
    if extracted_messages:
        print("[*] Extracted error message(s):")
        for message in extracted_messages:
            print(message)
            logging.info(f"[*] Extracted error message: {message}")
        return extracted_messages[0]
    else:
        print("[*] No error message found in the error.")
        logging.info("[*] No error message found in the error.")
        return None

def extract_urls(data):
    urls = []
    counter = 0
    for item in data.get('items',[]):
        link = item.get('link')
        if link:
            urls.append(link)
            counter += 1
            if counter >= 5:
                break
    open_urls(urls)
    print(f"[*] Extracted URLs: {urls}")
    for url in urls:
        logging.info(f"[*] Extracted URLs: {url}")
        
#Opens the extracted urls from the list and opens a new tab in an existing session (or new browser session of default browser if no existing) for each of the 5.
def open_urls(urls):
    for url in urls:
        webbrowser.open(url, new=0, autoraise=True)

# Queries stack exchange api /search? built as of 24SEPT2023 and retrieves the data in json format, finally passing it to the extract_urls function
def query_api(error_message):
    # reference docs from here: https://api.stackexchange.com/docs/search
    query_url = f"https://api.stackexchange.com/2.3/search?order=desc&sort=activity&intitle={error_message}&site=stackoverflow"
    response = requests.get(query_url)
    if response.status_code == 200:
        data = response.json()
        logging.info("[*] Stack Overflow API response received.")
        extract_urls(data)
    else:
        print("[*] Failed to retrieve Stack Overflow data.")
        print(f"[*] Status code: {response.status_code}")
        logging.error(f"[*] Failed to retrieve Stack Overflow data. Status code received from troubleshooting: {response.status_code}")

if __name__ == "__main__":
    main()