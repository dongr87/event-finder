import httpx
from bs4 import BeautifulSoup
from datetime import datetime, date
from model import Event
from typing import Optional


def fetch_crystal_events():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    # Added headers and follow_redirects to avoid 403 and handle URL changes
    url = 'https://www.crystalballroomboston.com/events/'
    print(f"fetching content from {url}...")

    try:
        response = httpx.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        events = soup.select('div#event-listings .event-grid-item')
        print(f"Found {len(events)} events")
        for event in events[:1]:
            # 1. get event title
            title_el = event.select_one('.entry-title')
            title = title_el.a.text.strip() if title_el else "Unknown Title"
            #2. Get link
            link = title_el.a['href'] if title_el else ""
            # 3. get event date/time
            date_icon = event.select_one('.fa-calendar')
            date_str = date_icon.next_sibling.strip() if date_icon and date_icon.next_sibling else ""
            time_icon = event.select_one('.fa-clock')
            time_str = time_icon.next_sibling.strip() if time_icon and time_icon.next_sibling else ""

            # parsing clean date
            clean_date = datetime.strptime(date_str, "%a, %b %d, %Y")
            
            raw_data = {
                "venue": "Crystal Ballroom",
                "title": title,
                "link": link,
                "start_time": clean_date,
                "raw_date_str": date_str
            }

            event_obj = Event(**raw_data)
    except httpx.HTTPError as e:
        print(f"fetching error: {e}")
    

def parse_rockwell_date(date_str: str):
    try:
        clean_str = date_str.replace('@', '').replace('  ', ' ')
        clean_str_with_year = f"{clean_str}, 2026"
        dt = datetime.strptime(clean_str_with_year, "%a, %B %d %I:%M %p, %Y")
        return dt
    except Exception as e:
        print(f"error parsing date: {e}")
        return None


def fetch_rockwell_events():
    url = "https://therockwell.org/calendar/month"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    print(f"fetching content from {url}...")

    try:
        response = httpx.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        events = soup.select('td.tribe-events-calendar-month__day')
        print(f"found {len(events)} events")

        for event in events[20:21]:
            articles = event.select('article.tribe-events-calendar-month__calendar-event')

            for article in articles:
                title_link = article.select_one('.tribe-events-calendar-month__calendar-event-title-link')
                title = title_link.get("title", '').strip() if title_link else "Unknown Title"
                link = title_link.get("href", '') if title_link else ""

                full_date_el = article.select_one('.tribe-event-date-start')
                full_date_str = full_date_el.text.strip() if full_date_el else ""

                raw_data = {
                    "venue": "Rockwell",
                    "title": title,
                    "link": link,
                    "start_time": parse_rockwell_date(full_date_str),
                    "raw_date_str": full_date_str
                }

                event_obj = Event(**raw_data)

    except httpx.HTTPError as e:
        print(f"fetching error: {e}")


if __name__ == "__main__":
    # fetch_crystal_events()
    fetch_rockwell_events()
