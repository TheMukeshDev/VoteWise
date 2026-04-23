from flask import Blueprint, request, jsonify, Response
from services.firestore_service import save_reminder
from services.calendar_service import create_voting_reminder
from utils.response_helper import success_response, error_response

reminder_bp = Blueprint('reminder', __name__)

@reminder_bp.route('/', methods=['POST'])
def set_reminder():
    data = request.json or {}
    user_id = data.get('user_id', 'anonymous')
    event_name = data.get('event_name')
    event_date = data.get('event_date')
    
    if not all([event_name, event_date]):
        return jsonify(*error_response("event_name and event_date are required"))
        
    # Save to DB if possible (might fail silently if no Firebase creds, handled inside save_reminder)
    save_reminder(user_id, data)
    
    # Generate Calendar Service .ics content
    ics_content = create_voting_reminder(event_name, event_date)
    
    if not ics_content:
        return jsonify(*error_response("Failed to generate calendar invite"))
        
    # Return as downloadable .ics file
    return Response(
        ics_content,
        mimetype="text/calendar",
        headers={"Content-disposition": f"attachment; filename=votewise_{event_date.replace(' ', '_')}.ics"}
    )
