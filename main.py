from scrapers import CrystalScraper, RockwellScraper

def main():
    scrapers = [
        CrystalScraper(),
        RockwellScraper()
    ]

    all_results = []

    print("--- start daily event fetching task ---")

    for scraper in scrapers:
        try:
            events = scraper.fetch()
            all_results.extend(events)
            print(f"Successuflly fetched {len(events)} events from {scraper.url}") 
        except Exception as e:
            print(f"error fetching {scraper.url}: {e}")

    all_results.sort(key=lambda x: x.start_time)

    print("\n--- performance list ---")
    for event in all_results:
        print(f"[{event.start_time.strftime('%Y-%m-%d %H:%M')}] @{event.venue.ljust(18)} | {event.title}")

if __name__ == "__main__":
    main()