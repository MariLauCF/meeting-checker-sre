import json
from pathlib import Path

from flask import Flask, jsonify, render_template_string

from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
MEETINGS_FILE = BASE_DIR / "meetings.json"

TOTAL_MEETINGS = Gauge(
    "meeting_checker_total_meetings",
    "Total number of monitored meetings",
)

READY_MEETINGS = Gauge(
    "meeting_checker_ready_meetings",
    "Number of meetings that are ready",
)

NOT_READY_MEETINGS = Gauge(
    "meeting_checker_not_ready_meetings",
    "Number of meetings that are not ready",
)

MISSING_ROOM = Gauge(
    "meeting_checker_missing_room_total",
    "Number of meetings without an assigned room",
)

PENDING_RSVP = Gauge(
    "meeting_checker_pending_rsvp_total",
    "Number of attendees with pending RSVP responses",
)

DECLINED_RSVP = Gauge(
    "meeting_checker_declined_rsvp_total",
    "Number of attendees who declined their invitation",
)

READINESS_PERCENTAGE = Gauge(
    "meeting_checker_readiness_percentage",
    "Percentage of monitored meetings that are ready",
)

def load_meetings():
    """Load meeting data from the local JSON file."""
    with open(MEETINGS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def check_meeting(meeting):
    """Evaluate whether a meeting is ready."""

    has_room = bool(meeting.get("room", "").strip())

    attendees = meeting.get("attendees", [])

    pending = [
        attendee["name"]
        for attendee in attendees
        if attendee.get("response") == "pending"
    ]

    declined = [
        attendee["name"]
        for attendee in attendees
        if attendee.get("response") == "declined"
    ]

    ready = has_room and not pending and not declined

    return {
        **meeting,
        "has_room": has_room,
        "pending": pending,
        "declined": declined,
        "ready": ready,
    }


def get_results():
    """Analyze all monitored meetings."""
    meetings = load_meetings()

    monitored_types = {"Daily Huddle", "Client Meeting"}

    monitored_meetings = [
        meeting
        for meeting in meetings
        if meeting.get("type") in monitored_types
    ]

    return [check_meeting(meeting) for meeting in monitored_meetings]

def update_metrics(results):
    """Update Prometheus metrics from the current meeting data."""

    total = len(results)
    ready = sum(1 for meeting in results if meeting["ready"])
    not_ready = total - ready

    missing_room = sum(
        1 for meeting in results if not meeting["has_room"]
    )

    pending_rsvp = sum(
        len(meeting["pending"]) for meeting in results
    )

    declined_rsvp = sum(
        len(meeting["declined"]) for meeting in results
    )

    readiness_percentage = (
        (ready / total) * 100 if total > 0 else 0
    )

    TOTAL_MEETINGS.set(total)
    READY_MEETINGS.set(ready)
    NOT_READY_MEETINGS.set(not_ready)
    MISSING_ROOM.set(missing_room)
    PENDING_RSVP.set(pending_rsvp)
    DECLINED_RSVP.set(declined_rsvp)
    READINESS_PERCENTAGE.set(readiness_percentage)

@app.route("/")
def home():
    results = get_results()

    total = len(results)
    ready = sum(1 for meeting in results if meeting["ready"])
    not_ready = total - ready

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Meeting Checker</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
                padding: 40px;
                color: #222;
            }

            .container {
                max-width: 1000px;
                margin: auto;
            }

            h1 {
                color: #161616;
            }

            .subtitle {
                color: #525252;
                margin-bottom: 30px;
            }

            .summary {
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }

            .summary-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                min-width: 180px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            }

            .number {
                font-size: 32px;
                font-weight: bold;
            }

            .meeting {
                background: white;
                margin-bottom: 18px;
                padding: 22px;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            }

            .ready {
                border-left: 7px solid #24a148;
            }

            .not-ready {
                border-left: 7px solid #da1e28;
            }

            .status-ready {
                color: #198038;
                font-weight: bold;
            }

            .status-not-ready {
                color: #da1e28;
                font-weight: bold;
            }

            .detail {
                margin: 6px 0;
            }
        </style>
    </head>

    <body>
        <div class="container">

            <h1>Meeting Checker</h1>

            <p class="subtitle">
                SRE Meeting Readiness Monitoring Application
            </p>

            <div class="summary">

                <div class="summary-card">
                    <div>Total Meetings</div>
                    <div class="number">{{ total }}</div>
                </div>

                <div class="summary-card">
                    <div>Ready</div>
                    <div class="number" style="color:#198038;">
                        {{ ready }}
                    </div>
                </div>

                <div class="summary-card">
                    <div>Not Ready</div>
                    <div class="number" style="color:#da1e28;">
                        {{ not_ready }}
                    </div>
                </div>

            </div>

            {% for meeting in meetings %}

            <div class="meeting {{ 'ready' if meeting.ready else 'not-ready' }}">

                <h2>{{ meeting.subject }}</h2>

                <div class="detail">
                    <strong>Type:</strong>
                    {{ meeting.type }}
                </div>

                <div class="detail">
                    <strong>Time:</strong>
                    {{ meeting.time }}
                </div>

                <div class="detail">
                    <strong>Room:</strong>
                    {{ meeting.room if meeting.has_room else 'NO ROOM ASSIGNED' }}
                </div>

                <div class="detail">
                    <strong>Pending RSVP:</strong>
                    {{ meeting.pending|join(', ') if meeting.pending else 'None' }}
                </div>

                <div class="detail">
                    <strong>Declined RSVP:</strong>
                    {{ meeting.declined|join(', ') if meeting.declined else 'None' }}
                </div>

                <p class="{{ 'status-ready' if meeting.ready else 'status-not-ready' }}">

                    {% if meeting.ready %}
                        READY
                    {% else %}
                        NOT READY
                    {% endif %}

                </p>

            </div>

            {% endfor %}

        </div>
    </body>
    </html>
    """

    return render_template_string(
        html,
        meetings=results,
        total=total,
        ready=ready,
        not_ready=not_ready,
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "service": "meeting-checker",
        }
    )

@app.route("/metrics")
def metrics():
    results = get_results()
    update_metrics(results)

    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
