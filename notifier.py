import requests
import json

def send_discord_notification(webhook_url, listing_data):
    """
    Sends a formatted Discord notification for a new apartment listing.

    Args:
        webhook_url (str): The Discord webhook URL.
        listing_data (dict): A dictionary containing the details of the listing.
    """
    if not webhook_url or "YOUR_WEBHOOK_URL_HERE" in webhook_url:
        print("Webhook URL not configured. Skipping notification.")
        return

    # Create the main structure of the embed
    embed = {
        "title": listing_data.get('title', 'N/A'),
        "url": listing_data.get('url', 'N/A'),
        "color": 15258703,  # A nice gold/yellow color
        "fields": [
            {
                "name": "Price",
                "value": listing_data.get('price', 'N/A'),
                "inline": True
            },
            {
                "name": "Area",
                "value": f"{listing_data.get('area', 'N/A')} m²",
                "inline": True
            },
            {
                "name": "Location",
                "value": listing_data.get('location', 'N/A'),
                "inline": False
            }
        ]
    }
    
    # Conditionally add extra details if they exist
    details_fields = [
        ("Offer Type", listing_data.get('offer_type')),
        ("Furnished", listing_data.get('furnished')),
        ("Pets Allowed", listing_data.get('pets')),
        ("Building Type", listing_data.get('building_type')),
        ("Additional Rent", listing_data.get('additional_rent'))
    ]

    for name, value in details_fields:
        if value:
            embed["fields"].append({"name": name, "value": value, "inline": True})

    # Only add the image if a valid URL exists
    image_url = listing_data.get('image_url')
    if image_url and image_url != 'N/A':
        embed["image"] = { "url": image_url }

    # Final payload to be sent to Discord
    data = { "embeds": [embed] }

    try:
        response = requests.post(webhook_url, json=data)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        print(f"Successfully sent notification for listing ID: {listing_data.get('id')}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord notification for listing ID {listing_data.get('id')}: {e}")
        # Add detailed logging to see the problematic payload and response
        print("--- Payload Sent ---")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("--- Discord Response ---")
        if e.response:
            print(e.response.text)
        print("----------------------") 