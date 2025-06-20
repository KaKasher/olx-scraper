import configparser
import json
from scraper import scrape_olx_listings, scrape_listing_details
from database import initialize_database, get_seen_listing_ids, add_listing_ids
from notifier import send_discord_notification

def main():
    """
    Main function to run the apartment scraper and notifier.
    """
    # Load configuration without interpolation to handle '%' in URLs
    config = configparser.ConfigParser(interpolation=None)
    config.read('config.ini')

    db_path = config.get('database', 'path')
    webhook_url = config.get('discord', 'webhook_url')
    scrape_details = config.getboolean('scraper', 'scrape_details', fallback=False)
    search_urls = dict(config.items('urls'))

    # Initialize the database
    initialize_database(db_path)

    # Get the set of IDs we've already seen
    seen_ids = get_seen_listing_ids(db_path)
    print(f"Loaded {len(seen_ids)} seen listing IDs from the database.")

    all_new_listings = []
    
    # Process each URL from the config file
    for name, url in search_urls.items():
        print(f"\nScraping {name}...")
        scraped_listings = scrape_olx_listings(url)
        
        new_listings_for_url = []
        new_ids_for_url = []

        # Identify which listings are new
        for listing in scraped_listings:
            if listing['id'] not in seen_ids:
                # If the feature is enabled, scrape the listing's page for more details,
                # but only if it's an OLX link.
                if scrape_details and listing.get('url') and "olx.pl" in listing['url']:
                    print(f"Scraping details for new listing: {listing['id']}...")
                    additional_details = scrape_listing_details(listing['url'])
                    listing.update(additional_details) # Merge the new details
                
                new_listings_for_url.append(listing)
                new_ids_for_url.append(listing['id'])
        
        if new_listings_for_url:
            print(f"Found {len(new_listings_for_url)} new listings for '{name}':")
            
            # Send a notification for each new listing
            for listing in new_listings_for_url:
                send_discord_notification(webhook_url, listing)
            
            # Add the new listings to our master list
            all_new_listings.extend(new_listings_for_url)
            
            # Update the database with the new IDs
            add_listing_ids(db_path, new_ids_for_url)
            print(f"Added {len(new_ids_for_url)} new listing IDs to the database.")
        else:
            print("No new listings found for this URL.")
            
    if not all_new_listings:
        print("\nNo new listings found across all URLs.")

if __name__ == '__main__':
    main() 