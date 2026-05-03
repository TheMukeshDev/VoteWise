"""
Google Calendar API Service for VoteWise AI

Provides voter reminder integration with Google Calendar.
Features:
- Add election reminders to Google Calendar
- Sync reminders from voter dashboard
- OAuth-based calendar access
- Reminder status tracking
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


def create_voting_reminder(event_name: str, event_date_str: str) -> Optional[str]:
    """
    Backward-compatible function for generating ICS reminder.
    (Legacy API for routes/reminder.py)
    """
    try:
        service = CalendarService()
        return service.generate_ics_file(
            summary=event_name,
            start_date=event_date_str,
            description=f"Election reminder from VoteWise AI: {event_name}",
        )
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.warning("Error generating reminder: %s", e)
        return None


class CalendarService:
    """Google Calendar API integration for voter reminders."""

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self.scope = "https://www.googleapis.com/auth/calendar.events"

    def create_election_reminder(
        self,
        summary: str,
        start_date: str,
        end_date: Optional[str] = None,
        description: str = ", ",
        location: str = ", ",
        reminder_type: str = "election",
    ) -> Optional[dict[str, Any]]:
        """
        Create an election reminder event in Google Calendar.

        Args:
            summary: Event title
            start_date: Start date (ISO format or YYYY-MM-DD)
            end_date: End date (optional)
            description: Event description
            location: Event location
            reminder_type: Type of reminder (registration, polling, result)

        Returns:
            Created event data or None
        """
        if not self.access_token:
            return self._create_local_reminder(summary, start_date, description)

        start_dt = self._parse_date(start_date)
        end_dt = (
            end_date and self._parse_date(end_date) or start_dt + timedelta(hours=4)
        )

        event = {
            "summary": summary,
            "description": description
            or f"Election reminder from VoteWise AI: {summary}",
            "location": location,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Kolkata"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60 * 7},  # 1 week before
                    {"method": "popup", "minutes": 24 * 60},  # 1 day before
                ],
            },
            "colorId": self._get_color_for_type(reminder_type),
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                f"{self.base_url}/calendars/primary/events",
                headers=headers,
                json=event,
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            logger.warning("Calendar API Error: %s", e)

        return self._create_local_reminder(summary, start_date, description)

    def create_registration_reminder(self, deadline: str) -> Optional[dict[str, Any]]:
        """
        Create voter registration deadline reminder.

        Args:
            deadline: Registration deadline date

        Returns:
            Event data
        """
        return self.create_election_reminder(
            summary="🔴 Voter Registration Deadline",
            start_date=deadline,
            description=(
                "Final date to register as a voter for upcoming elections. ",
                "Visit: https://voteswise.ai to complete your registration.",
            ),
            reminder_type="registration",
        )

    def create_polling_reminder(
        self, polling_date: str, booth_location: str = ", "
    ) -> Optional[dict[str, Any]]:
        """
        Create polling day reminder.

        Args:
            polling_date: Election day date
            booth_location: Polling booth address

        Returns:
            Event data
        """
        return self.create_election_reminder(
            summary="🗳️ Election Day - VOTE!",
            start_date=polling_date,
            description=(
                f"It's time to vote! Your voice matters. "
                f"Polling booth: {booth_location or 'Check your voter ID for details'}. ",
                "Don't forget to carry a valid ID proof.",
            ),
            location=booth_location,
            reminder_type="polling",
        )

    def create_result_reminder(self, result_date: str) -> Optional[dict[str, Any]]:
        """
        Create election result announcement reminder.

        Args:
            result_date: Result announcement date

        Returns:
            Event data
        """
        return self.create_election_reminder(
            summary="📊 Election Results Announcement",
            start_date=result_date,
            description=(
                "Election results will be announced today. ",
                "Stay informed about the outcome: https://votewise.ai",
            ),
            reminder_type="result",
        )

    def get_upcoming_events(self, max_results: int = 10) -> list[dict[str, Any]]:
        """
        Get upcoming calendar events.

        Args:
            max_results: Maximum events to return

        Returns:
            list of events
        """
        if not self.access_token:
            return []

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(
                f"{self.base_url}/calendars/primary/events"
                f"?maxResults={max_results}"
                f"&orderBy=startTime"
                f"&singleEvents=true"
                f"&timeMin={now}",
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("items", [])
        except requests.RequestException:
            pass

        return []

    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.

        Args:
            event_id: Event ID to delete

        Returns:
            True if successful
        """
        if not self.access_token:
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.delete(
                f"{self.base_url}/calendars/primary/events/{event_id}",
                headers=headers,
                timeout=10,
            )
            return response.status_code in [200, 204]
        except requests.RequestException:
            pass

        return False

    def generate_ics_file(
        self,
        summary: str,
        start_date: str,
        end_date: Optional[str] = None,
        description: str = ", ",
        location: str = ", ",
    ) -> str:
        """
        Generate ICS file content for manual calendar import.

        Args:
            summary: Event title
            start_date: Start date
            end_date: End date (optional)
            description: Event description
            location: Event location

        Returns:
            ICS file content string
        """
        start_dt = self._parse_date(start_date)
        end_dt = (
            end_date and self._parse_date(end_date) or start_dt + timedelta(hours=4)
        )

        ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//VoteWise AI//Election Guide//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
DTSTAMP:{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}
DTSTART:{start_dt.strftime("%Y%m%dT%H%M%S")}
DTEND:{end_dt.strftime("%Y%m%dT%H%M%S")}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""

        return ics

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime."""
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%b %d, %Y",
            "%B %d, %Y",
            "%d-%m-%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return datetime.now() + timedelta(days=14)

    def _get_color_for_type(self, reminder_type: str) -> str:
        """Get calendar color ID for reminder type."""
        colors = {
            "registration": "9",  # Red
            "polling": "10",  # Green
            "result": "5",  # Blue
            "election": "6",  # Purple
            "custom": "7",  # Gray
        }
        return colors.get(reminder_type, "7")

    def _create_local_reminder(
        self, summary: str, start_date: str, description: str
    ) -> dict[str, Any]:
        """Create local reminder when API unavailable."""
        return {
            "kind": "calendar#event",
            "summary": summary,
            "description": description,
            "status": "confirmed",
            "start_date": start_date,
            "htmlLink": f"data:text/calendar,{summary}",
            "icalUID": f"local-{datetime.now().timestamp()}",
        }


class LocalCalendarService:
    """Local calendar service for voters not using Google OAuth."""

    @staticmethod
    def generate_voting_calendar(
        title: str, date: str, reminder_type: str = "polling"
    ) -> str:
        """Generate ICS for voter calendar."""
        service = CalendarService()
        return service.generate_ics_file(
            summary=title, start_date=date, description=f"VoteWise AI reminder: {title}"
        )


calendar_service = CalendarService()
local_calendar_service = LocalCalendarService()
