import requests
import json
import schedule
import time
from slack_sdk import WebClient

# Initialize the Slack API client
client = WebClient(token="SLACK_BOT_TOKEN")

# Replace with your Linode API token
api_token = "API_TOKEN"

def fetch_and_post_tickets():
    response = requests.get(
        'https://api.linode.com/v4/support/tickets',
        headers={'Authorization': f'Bearer {api_token}'}
    )

    if response.status_code == 200:
        # Parse the JSON response into a dictionary
        tickets = response.json()["data"]  # Assuming "data" contains the list of tickets
        open_tickets = [ticket for ticket in tickets if ticket["status"] == "open"]

        if open_tickets:
            for ticket in open_tickets:
                ticket_id = ticket["id"]
                ticket_status = ticket["status"]
                ticket_url = f'https://cloud.linode.com/support/tickets/{ticket_id}'  # Replace with the actual URL structure
                # Send a message to the #tickets channel for each open ticket
                response = client.chat_postMessage(
                    channel="#tickets",
                    text=f"Hi! The status of ticket {ticket_id} is {ticket_status}. Example ticket URL: <{ticket_url}|View Ticket>"
                )
                # Check if the message was sent successfully
                if response["ok"]:
                    print(f"Message sent successfully for open ticket {ticket_id}!")
                else:
                    if "errors" in response and response["errors"][0]["reason"] == "Invalid Token":
                        print("Invalid API token. Please check your token.")
                    else:
                        print(f"Failed to send message for open ticket {ticket_id}:", response["error"])
        else:
            # Post a message to the #tickets channel indicating that there are no open tickets
            response = client.chat_postMessage(
                channel="#tickets",
                text="No open tickets at the moment."
            )
            # Check if the message was sent successfully
            if response["ok"]:
                print("Message sent successfully: No open tickets.")
            else:
                if "errors" in response and response["errors"][0]["reason"] == "Invalid Token":
                    print("Invalid API token. Please check your token.")
                else:
                    print("Failed to send message:", response["error"])

        # Handle the case where the API token is invalid
        if response.status_code == 401:
            print("Invalid API token. Please check your token.")
    else:
        print(f'Failed to get tickets: {response.content}')


# Execute the function immediately
fetch_and_post_tickets()

# Schedule the script to run every hour
schedule.every().hour.do(fetch_and_post_tickets)

while True:
    schedule.run_pending()
    time.sleep(1)
