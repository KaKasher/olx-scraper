import requests
from bs4 import BeautifulSoup
import json

def scrape_listing_details(url):
    """
    Scrapes a single listing page for additional details.
    
    Args:
        url (str): The URL of the listing page.
        
    Returns:
        dict: A dictionary with the additional details found.
    """
    if "olx.pl" not in url:
        return {} # Not an OLX link, so we don't scrape

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    details = {}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scrape the main image from the details page.
        image_gallery = soup.find('div', {'data-testid': 'image-galery-container'})
        if image_gallery:
            image_element = image_gallery.find('img')
            # Ensure we get a valid, absolute URL for the image.
            if image_element and image_element.get('src') and image_element.get('src').startswith('https://'):
                details['image_url'] = image_element['src']
        
        params_container = soup.find('div', {'data-testid': 'ad-parameters-container'})
        if params_container:
            params = params_container.find_all('p')
            for p in params:
                text = p.text
                if ":" in text:
                    key, value = text.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "Zwierzęta":
                        details['pets'] = value
                    elif key == "Umeblowane":
                        details['furnished'] = value
                    elif key == "Rodzaj zabudowy":
                        details['building_type'] = value
                    elif key == "Czynsz (dodatkowo)":
                        details['additional_rent'] = value
                elif "Prywatne" in text:
                    details['offer_type'] = "Private"
                elif "Firmowe" in text or "Agencja" in text:
                    details['offer_type'] = "Business"
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details from {url}: {e}")
    except Exception as e:
        print(f"Error parsing details on page {url}: {e}")
        
    return details

def scrape_olx_listings(url):
    """
    Scrapes a given OLX search results page for apartment listings.

    Args:
        url (str): The URL of the OLX search results page.

    Returns:
        list: A list of dictionaries, where each dictionary represents a listing.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    listings = []
    
    # All listing cards are contained in a div with data-cy="l-card"
    cards = soup.find_all('div', {'data-cy': 'l-card'})

    for card in cards:
        # Check for and skip promoted listings.
        # As you identified, they contain a div with class 'css-qavd0c'.
        if card.find('div', class_='css-qavd0c'):
            continue

        # Some "cards" might not be actual listings (e.g., ad placeholders).
        # We'll check for an ID, as real listings should have one.
        if not card.get('id'):
            continue

        listing_data = {}
        
        try:
            listing_data['id'] = card.get('id')
            
            title_element = card.find('h4')
            listing_data['title'] = title_element.text.strip() if title_element else 'N/A'

            price_element = card.find('p', {'data-testid': 'ad-price'})
            listing_data['price'] = price_element.text.strip() if price_element else 'N/A'
            
            # Find the primary link element for the listing
            url_element = card.find('a', class_='css-1tqlkj0')
            if url_element and url_element.get('href'):
                href = url_element['href']
                # Case 1: It's an absolute URL (e.g., to Otodom)
                if href.startswith('https://'):
                    listing_data['url'] = href
                # Case 2: It's a relative URL for an OLX listing
                elif href.startswith('/d/oferta/'):
                    listing_data['url'] = 'https://www.olx.pl' + href
                else:
                    listing_data['url'] = 'N/A' # Unrecognized format
            else:
                listing_data['url'] = 'N/A' # No link found

            location_element = card.find('p', {'data-testid': 'location-date'})
            if location_element:
                full_location_text = location_element.text.strip()
                # The location and date are separated by " - "
                listing_data['location'] = full_location_text.split(' - ')[0].strip()
            else:
                listing_data['location'] = 'N/A'
            
            # Extract square meters. The text contains "m²" within a specific span.
            # Let's target the class 'css-6as4g5' which seems to hold the area info.
            area_element = card.find('span', class_='css-6as4g5')
            if area_element and 'm²' in area_element.text:
                # Extract the numeric part from a string like "28 m²"
                listing_data['area'] = area_element.text.replace('m²', '').strip()
            else:
                listing_data['area'] = 'N/A'
            
            # A valid listing must have an ID and a URL.
            if listing_data.get('id') and listing_data.get('url') != 'N/A':
                 listings.append(listing_data)

        except Exception as e:
            print(f"Error parsing a listing card with id={card.get('id')}: {e}")
            continue

    return listings

if __name__ == '__main__':
    # URL from the project plan for testing
    test_url = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/krakow/?search%5Border%5D=created_at:desc&search%5Bfilter_float_price:to%5D=4500"
    
    scraped_listings = scrape_olx_listings(test_url)
    
    print(f"Found {len(scraped_listings)} listings.")
    
    # Pretty print the first 3 listings for verification
    for listing in scraped_listings[:3]:
        # Use json for clean, readable output
        print(json.dumps(listing, indent=4, ensure_ascii=False)) 