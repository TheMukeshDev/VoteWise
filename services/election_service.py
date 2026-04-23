from services.firestore_service import get_election_process_data, get_faqs_data, get_timeline_data

def get_election_process():
    """
    Returns the step-by-step election process.
    If Firestore is empty/unavailable, return fallback data.
    """
    data = get_election_process_data()
    if not data:
        return [
            {"step": 1, "title": "Voter Registration", "description": "Register yourself as a voter to get your Voter ID."},
            {"step": 2, "title": "Name Verification", "description": "Check if your name appears in the voter list."},
            {"step": 3, "title": "Election Announcement", "description": "Election authority announces the dates."},
            {"step": 4, "title": "Voting Day", "description": "Go to the polling booth, verify identity, and cast your vote."},
            {"step": 5, "title": "Results", "description": "Votes are counted and results declared."}
        ]
    return data

def get_faqs():
    data = get_faqs_data()
    if not data:
        return [
            {"question": "Who can vote?", "answer": "Any citizen aged 18 or above can vote."},
            {"question": "What documents are needed?", "answer": "Voter ID card or a valid government ID like Aadhar/Passport."}
        ]
    return data

def get_timeline():
    data = get_timeline_data()
    if not data:
        return [
            {"date": "2024-03-01", "event": "Voter Registration Deadline"},
            {"date": "2024-04-15", "event": "Voting Day"},
            {"date": "2024-05-01", "event": "Results Declared"}
        ]
    return data
