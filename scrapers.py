import httpx
from bs4 import BeautifulSoup
from datetime import datetime, date
from model import Event
from typing import Optional

class BaseScraper:
    "Base class, to store general headers or methods"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

class CrystalScraper(BaseScraper):
    url = "https://www.crystalballroomboston.com/events/"

    def fetch(self) -> list[Event]:
        parsed_events = []
        print(f"fetching content from {self.url}...")
        response = httpx.get(self.url, headers=self.headers, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        events = soup.select('div#event-listings .event-grid-item')

        for event in events:
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
            
            event = Event(
                venue="Crystal Ballroom",
                title=title,
                link=link,
                start_time=clean_date,
                raw_date_str=date_str
            )
            parsed_events.append(event)

        return parsed_events


class RockwellScraper(BaseScraper):
    url = "https://therockwell.org/calendar/month"

    def _parse_date(self, date_str: str):
        """
        Example format: Thu, February 5 @ 7:00 pm
        """
        clean_str = date_str.replace('@', '').replace('  ', ' ')
        clean_str_with_year = f"{clean_str}, 2026"
        dt = datetime.strptime(clean_str_with_year, "%a, %B %d %I:%M %p, %Y")
        return dt

    def fetch(self) -> list[Event]:
        parsed_events = []
        print(f"fetching content from {self.url}...")

        response = httpx.get(self.url, headers=self.headers, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        events = soup.select('td.tribe-events-calendar-month__day')

        for event in events:
            articles = event.select('article.tribe-events-calendar-month__calendar-event')

            for article in articles:
                title_link = article.select_one('.tribe-events-calendar-month__calendar-event-title-link')
                title = title_link.get("title", '').strip() if title_link else "Unknown Title"
                link = title_link.get("href", '') if title_link else ""

                full_date_el = article.select_one('.tribe-event-date-start')
                full_date_str = full_date_el.text.strip() if full_date_el else ""

                event = Event(
                    venue="Rockwell",
                    title=title,
                    link=link,
                    start_time=self._parse_date(full_date_str),
                    raw_date_str=full_date_str
                )
                parsed_events.append(event)

        return parsed_events