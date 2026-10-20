
"""Local dashboard for the eRaksha prototype."""

from flask import Flask, jsonify, render_template_string

from eraksha.database import get_connection, initialize_database
from eraksha.device_inventory import list_devices


app = Flask(__name__)

DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>eRaksha | IoT Security</title>
    <style>
        body {
            font-family: system-ui, sans-serif;
            max-width: 1100px;
            margin: 40px auto;
            padding: 0 20px;
            background: #101827;
            color: #edf2f7;
        }
        h1 { color: #7dd3fc; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }
        .card {
            padding: 20px;
            border: 1px solid #334155;
            border-radius: 12px;
            background: #1e293b;
        }
        .number { font-size: 2rem; font-weight: 700; }
        .muted { color: #cbd5e1; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td {
            padding: 12px;
            border-bottom: 1px solid #334155;
            text-align: left;
            overflow-wrap: anywhere;
        }
        .notice {
            background: #422006;
            color: #fde68a;
            padding: 12px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <h1>eRaksha IoT Security</h1>
    <p class="muted">Prototype monitoring dashboard</p>
    <p class="notice">
        Demo mode: device discovery and traffic may be simulated.
        An anomaly is a review signal, not proof of an attack.
    </p>

    <div class="grid">
        <section class="card">
            <div class="muted">Devices</div>
            <div class="number">{{ device_count }}</div>
        </section>
        <section class="card">
            <div class="muted">Stored flows</div>
            <div class="number">{{ flow_count }}</div>
        </section>
        <section class="card">
            <div class="muted">Flagged flows</div>
            <div class="number">{{ anomaly_count }}</div>
        </section>
    </div>

    <h2>Anomaly alerts</h2>
    <p class="muted">
        Highest anomaly-strength scores first. Flags require investigation
        and do not establish that an attack occurred.
    </p>
    <table>
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>Source IP</th>
                <th>Destination</th>
                <th>Protocol</th>
                <th>Score</th>
                <th>Explanation</th>
                <th>Data source</th>
            </tr>
        </thead>
        <tbody>
        {% for alert in alerts %}
            <tr>
                <td>{{ alert.timestamp }}</td>
                <td>{{ alert.src_ip }}</td>
                <td>{{ alert.dst_ip }}:{{ alert.dst_port or "—" }}</td>
                <td>{{ alert.protocol }}</td>
                <td>{{ "%.3f"|format(alert.anomaly_score or 0) }}</td>
                <td>{{ alert.explanation or "No explanation recorded" }}</td>
                <td>{{ alert.source }}</td>
            </tr>
        {% else %}
            <tr><td colspan="7">No flagged flows recorded.</td></tr>
        {% endfor %}
        </tbody>
    </table>


    <h2>Device inventory</h2>
    <table>
        <thead>
            <tr>
                <th>IP address</th>
                <th>Hostname</th>
                <th>Vendor</th>
                <th>Source</th>
            </tr>
        </thead>
        <tbody>
        {% for device in devices %}
            <tr>
                <td>{{ device.ip_address }}</td>
                <td>{{ device.hostname or "Unknown" }}</td>
                <td>{{ device.vendor or "Unknown" }}</td>
                <td>{{ device.source }}</td>
            </tr>
        {% else %}
            <tr><td colspan="4">No devices recorded yet.</td></tr>
        {% endfor %}
        </tbody>
    </table>

    <p class="muted">
        JSON status endpoint: <a href="/api/status">/api/status</a>
    </p>
</body>
</html>
"""


@app.get("/")
def index():
    initialize_database()
    devices = list_devices()

    with get_connection() as connection:
        flow_count = connection.execute(
            "SELECT COUNT(*) FROM flows"
        ).fetchone()[0]

        anomaly_count = connection.execute(
            "SELECT COUNT(*) FROM flows WHERE is_anomaly = 1"
        ).fetchone()[0]

        alert_rows = connection.execute(
            """
            SELECT timestamp, src_ip, dst_ip, dst_port,
                   protocol, anomaly_score, explanation, source
            FROM flows
            WHERE is_anomaly = 1
            ORDER BY anomaly_score DESC, timestamp DESC
            LIMIT 20
            """
        ).fetchall()

    alerts = [dict(row) for row in alert_rows]

    return render_template_string(
        DASHBOARD_HTML,
        devices=devices,
        device_count=len(devices),
        flow_count=flow_count,
        anomaly_count=anomaly_count,
        alerts=alerts,
    )


@app.get("/api/status")
def api_status():
    initialize_database()
    devices = list_devices()

    with get_connection() as connection:
        flow_count = connection.execute(
            "SELECT COUNT(*) FROM flows"
        ).fetchone()[0]
        anomaly_count = connection.execute(
            "SELECT COUNT(*) FROM flows WHERE is_anomaly = 1"
        ).fetchone()[0]

    return jsonify({
        "device_count": len(devices),
        "flow_count": flow_count,
        "flagged_flow_count": anomaly_count,
        "device_sources": {
            source: sum(
                device["source"] == source for device in devices
            )
            for source in ("simulated", "observed")
        },
        "mode": "prototype",
    })


def main():
    # Loopback only: the dashboard is not exposed to your LAN.
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
