import json
import requests
from bs4 import BeautifulSoup


def get_data(train_number):
    URL = (
        f"https://www.goibibo.com/trains/app/trainstatus/results/?train={train_number}"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }
    r = requests.get(URL, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        script = soup.find("script")
        if script:
            return json.loads(script.text.strip().split("=", 1)[1].strip(";"))
        else:
            return "Train not found"
    else:
        return "Invalid request"


if __name__ == "__main__":
    train_number = input("Enter train number: ")
    op = get_data(train_number)
    with open("out.json", "w") as f:
        json.dump(op, f)
