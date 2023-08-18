import re
import webbrowser
import requests
from bs4 import BeautifulSoup


def search_on_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    top_result = soup.find("div", class_="BNeawe").text
    print(top_result)


# Example usage
query = input("Enter a query: ")
search_on_google(query)


import webbrowser

def open_whatsapp():
    url = "https://web.whatsapp.com/"
    webbrowser.open(url)
    print("Opening WhatsApp...")

while True:
    command = input("Enter your command: ")
    if command.lower() == "open whatsapp":
        open_whatsapp()
        break
    else:
        print("Sorry, I don't understand that command.")

