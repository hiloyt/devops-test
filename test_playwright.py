import json
from playwright.sync_api import sync_playwright


def test_api():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            # Test Endpoint 1: Transactions made in the last 30 days
            page.goto("http://localhost:5000/transactions/30")
            response = json.loads(page.inner_text("body"))
            if isinstance(response, list):
                print("Endpoint 1 Result: success")
            else:
                print("Endpoint 1 Result: error")

            # Test Endpoint 2: Transactions count with Visa card type
            page.goto("http://localhost:5000/transactions/30/card/Visa")
            response = json.loads(page.inner_text("body"))
            if isinstance(response, dict) and "count" in response:
                print("Endpoint 2 Result: success")
            else:
                print("Endpoint 2 Result: error")

            # Test Endpoint 3: Transactions with specific country origin
            page.goto("http://localhost:5000/transactions/30/country/USA")
            response = json.loads(page.inner_text("body"))
            if isinstance(response, list):
                print("Endpoint 3 Result: success")
            else:
                print("Endpoint 3 Result: error")

            # Test Endpoint 4: Transactions within an amount range between 50.0 to 800.0
            page.goto("http://localhost:5000/transactions/30/amount/50.0/800.0")
            response = json.loads(page.inner_text("body"))
            if isinstance(response, list):
                print("Endpoint 4 Result: success")
            else:
                print("Endpoint 4 Result: error")

        # Error when REST API is unavailable
        except Exception as e:
            print("Error: RESTful API is unavailable")

        browser.close()


if __name__ == "__main__":
    test_api()
