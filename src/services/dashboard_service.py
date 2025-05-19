from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import desc # Import desc for ordering
from ..models.whiteboard_note import DatedNote # Changed from WhiteboardNote
import logging
from typing import List, Optional # Import List and Optional
from datetime import date as DateObject, datetime # Import date as DateObject to avoid conflict if datetime.date is used

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self, engine):
        """Initializes the service with an SQLAlchemy engine."""
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def get_notes_for_date(self, target_date: DateObject) -> List[DatedNote]:
        """Retrieves all notes for a specific date, ordered by creation time (latest first)."""
        with self.Session() as session:
            try:
                notes = session.query(DatedNote).filter(DatedNote.note_date == target_date).order_by(DatedNote.created_at.desc()).all()
                return notes
            except Exception as e:
                logger.error(f"Error fetching notes for date {target_date}: {e}")
                return []

    def get_latest_note_for_date(self, target_date: DateObject) -> Optional[DatedNote]:
        """Retrieves the most recent note for a specific date."""
        with self.Session() as session:
            try:
                note = session.query(DatedNote).filter(DatedNote.note_date == target_date).order_by(DatedNote.created_at.desc()).first()
                return note
            except Exception as e:
                logger.error(f"Error fetching latest note for date {target_date}: {e}")
                return None

    def save_note_for_date(self, content: str, note_date: DateObject) -> Optional[DatedNote]:
        """Saves a new note for a specific date."""
        with self.Session() as session:
            try:
                new_note = DatedNote(content=content, note_date=note_date)
                session.add(new_note)
                session.commit()
                session.refresh(new_note)
                return new_note
            except Exception as e:
                logger.error(f"Error saving note for date {note_date}: {e}")
                session.rollback()
                return None

    def delete_note(self, note_id: int) -> bool:
        """Deletes a specific note by its ID."""
        with self.Session() as session:
            try:
                note = session.query(DatedNote).filter(DatedNote.id == note_id).first()
                if note:
                    session.delete(note)
                    session.commit()
                    return True
                logger.warning(f"Note with id {note_id} not found for deletion.")
                return False
            except Exception as e:
                logger.error(f"Error deleting note with id {note_id}: {e}")
                session.rollback()
                return False

    def get_all_notes(self) -> List[DatedNote]:
        """Retrieves all notes, ordered by date and then creation time (latest first)."""
        with self.Session() as session:
            try:
                notes = session.query(DatedNote).order_by(DatedNote.note_date.desc(), DatedNote.created_at.desc()).all()
                return notes
            except Exception as e:
                logger.error(f"Error fetching all notes: {e}")
                return []

    def get_notes_in_period(self, start_date: DateObject, end_date: DateObject) -> List[DatedNote]:
        """Retrieves all notes within a given date range, inclusive."""
        with self.Session() as session:
            try:
                notes = session.query(DatedNote).filter(
                    DatedNote.note_date >= start_date,
                    DatedNote.note_date <= end_date
                ).order_by(DatedNote.note_date.asc(), DatedNote.created_at.asc()).all()
                return notes
            except Exception as e:
                logger.error(f"Error fetching notes in period {start_date} to {end_date}: {e}")
                return [] 