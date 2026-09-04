import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        brand_blue = colors.HexColor("#0D47A1")
        text_gray = colors.HexColor("#666666")
        light_border = colors.HexColor("#E0E0E0")

        # Top Header (Only pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(brand_blue)
            self.drawString(40, 815, "SINEXUS EDGE — MONITORING & LOGGING GUIDE (SINEXUS SIDE)")
            self.setFont("Helvetica", 8)
            self.setFillColor(text_gray)
            self.drawRightString(555, 815, "Final Delivery Document")
            
            self.setStrokeColor(light_border)
            self.setLineWidth(0.5)
            self.line(40, 808, 555, 808)

        # Bottom Footer (All Pages)
        self.setStrokeColor(light_border)
        self.setLineWidth(0.5)
        self.line(40, 45, 555, 45)

        self.setFont("Helvetica", 8)
        self.setFillColor(text_gray)
        self.drawString(40, 32, "Confidential — System Monitoring & Logging Specifications")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 32, page_str)

        self.restoreState()

def build_pdf(filename="Sinexus_Edge_Monitoring_and_Logging_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    c_primary = colors.HexColor("#0D47A1")     # Deep Blue
    c_secondary = colors.HexColor("#00838F")   # Teal
    c_accent = colors.HexColor("#1565C0")      # Bright Blue Accent
    c_dark = colors.HexColor("#212121")        # Dark Neutral
    c_light_bg = colors.HexColor("#F4F6F8")    # Light Neutral Background
    c_border = colors.HexColor("#CFD8DC")      # Border Gray
    c_white = colors.HexColor("#FFFFFF")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_white,
        spaceAfter=4
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1A237E")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_white
    )

    story = []

    # Title Banner Block
    banner_data = [[
        Paragraph("<b>SINEXUS EDGE MONITORING SYSTEM</b><br/><font size=12 color='#90CAF9'>System Monitoring & Logging Guide (Sinexus Side)</font>", title_style),
    ]]
    banner_table = Table(banner_data, colWidths=[515])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_primary),
        ('PADDING', (0, 0), (-1, -1), 14),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 12))

    # Meta Table
    meta_data = [
        [Paragraph("<b>System Name:</b> Sinexus Edge Monitoring Platform", body_style), Paragraph("<b>Document Type:</b> Monitoring & Logging Guide", body_style)],
        [Paragraph("<b>Target Infrastructure:</b> AWS Lightsail VPS (Ubuntu)", body_style), Paragraph("<b>Target Team:</b> Sinexus Operations & DevOps", body_style)],
        [Paragraph("<b>Log Daemon:</b> PM2 LogRotate Module", body_style), Paragraph("<b>Document Version:</b> 1.0.0 (Production)", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[257, 258])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 1. Executive Summary & Logging Architecture
    story.append(Paragraph("1. Executive Summary & Logging Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    exec_p = (
        "The <b>System Monitoring & Logging Guide (Sinexus Side)</b> defines operational standards for monitoring Node.js backend services, "
        "tracking system log streams, configuring PM2 log rotation, auditing compliance logs (`ConsentLog`), and monitoring real-time Socket.IO WebSockets."
    )
    story.append(Paragraph(exec_p, body_style))
    story.append(Spacer(1, 10))

    # Log Channels Table
    story.append(Paragraph("<b>System Logging Channels:</b>", h2_style))
    log_ch_data = [
        [Paragraph("Log Channel", table_header_style), Paragraph("Storage / Location", table_header_style), Paragraph("Logged Content & Operational Purpose", table_header_style)],
        [Paragraph("<b>Application Stdout Logs</b>", table_cell_style), Paragraph("<code>~/.pm2/logs/monitoring_system-out.log</code>", table_cell_style), Paragraph("HTTP access requests, API response status codes, Socket.IO client connections, and system initialization events.", table_cell_style)],
        [Paragraph("<b>Application Error Logs</b>", table_cell_style), Paragraph("<code>~/.pm2/logs/monitoring_system-error.log</code>", table_cell_style), Paragraph("Unhandled exceptions, stack traces, MongoDB database errors, and third-party API connection failures (Google Maps, FCM).", table_cell_style)],
        [Paragraph("<b>Compliance Audit Logs</b>", table_cell_style), Paragraph("MongoDB <code>ConsentLog</code> Collection", table_cell_style), Paragraph("Immutable record of user consent for Terms & Privacy policy, capturing user ID, IP address, User Agent, and timestamp.", table_cell_style)],
        [Paragraph("<b>Task Timeline Audit Logs</b>", table_cell_style), Paragraph("MongoDB <code>Task.timeline</code> Field", table_cell_style), Paragraph("Audit history logging every cleaning task state transition (<code>ASSIGNED</code> --> <code>IN_PROGRESS</code> --> <code>SUBMITTED</code> --> <code>VERIFIED</code>).", table_cell_style)],
        [Paragraph("<b>IoT Telemetry Sensor Data</b>", table_cell_style), Paragraph("MongoDB <code>SensorData</code> Collection", table_cell_style), Paragraph("Raw historical log stream of Odor levels (ppm), Footfall counters, and Feedback metrics per facility node.", table_cell_style)],
    ]
    log_ch_table = Table(log_ch_data, colWidths=[120, 155, 240])
    log_ch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(log_ch_table)
    story.append(Spacer(1, 14))

    # 2. PM2 Log Management & Log Rotation Setup
    story.append(Paragraph("2. PM2 Log Management & Rotation Setup", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    pm2_logs = [
        "<b>Installing PM2 LogRotate:</b> Execute <code>pm2 install pm2-logrotate</code> on AWS Lightsail terminal.",
        "<b>Maximum Log Size:</b> Configure max log file size to 10 MB: <code>pm2 set pm2-logrotate:max_size 10M</code>.",
        "<b>Log Retention Period:</b> Retain rotated logs for 14 days: <code>pm2 set pm2-logrotate:retain 14</code>.",
        "<b>Gzip Compression:</b> Enable log file compression to save disk space: <code>pm2 set pm2-logrotate:compress true</code>.",
        "<b>Flushing Active Logs:</b> To clear old log files manually, run <code>pm2 flush</code>."
    ]
    for p in pm2_logs:
        story.append(Paragraph(f"• {p}", bullet_style))
    story.append(Spacer(1, 14))

    # Page Break for clean layout
    story.append(PageBreak())

    # 3. Real-time System Health Monitoring
    story.append(Paragraph("3. Real-Time System Health Monitoring Guidelines", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    mon_data = [
        [Paragraph("Health Subsystem", table_header_style), Paragraph("Monitoring Tool / Command", table_header_style), Paragraph("Thresholds & Warning Signals", table_header_style)],
        [Paragraph("<b>Process Memory (RSS)</b>", table_cell_style), Paragraph("<code>pm2 monit</code>", table_cell_style), Paragraph("<font color='#E65100'><b>Warning:</b></font> Memory > 400 MB.<br/><font color='#C62828'><b>Critical:</b></font> Memory > 500 MB (Auto Restart).", table_cell_style)],
        [Paragraph("<b>CPU Utilization</b>", table_cell_style), Paragraph("<code>pm2 monit</code> / <code>htop</code>", table_cell_style), Paragraph("<font color='#E65100'><b>Warning:</b></font> Sustained CPU > 75% for 5 mins.", table_cell_style)],
        [Paragraph("<b>MongoDB Pool Health</b>", table_cell_style), Paragraph("MongoDB Atlas Metrics Dashboard", table_cell_style), Paragraph("Connection Pool Limit = 10 connections. Slow queries > 100ms.", table_cell_style)],
        [Paragraph("<b>WebSocket Engine</b>", table_cell_style), Paragraph("Application Logs", table_cell_style), Paragraph("Monitor WebSocket ping/pong latency and client connection spikes.", table_cell_style)],
    ]
    mon_table = Table(mon_data, colWidths=[120, 160, 235])
    mon_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(mon_table)
    story.append(Spacer(1, 14))

    # 4. Operations Incident Playbook
    story.append(Paragraph("4. Sinexus Operations Incident Response Playbook", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    playbook_steps = [
        "<b>Step 1 — Immediate Error Log Extraction:</b> When an operational issue is flagged, run <code>pm2 logs monitoring_system --err --lines 100</code> to extract the exact failure stack trace.",
        "<b>Step 2 — Database Connectivity Check:</b> Verify MongoDB Atlas connection string and network access IP whitelist if database errors occur.",
        "<b>Step 3 — Node Syntax Check:</b> Before applying patches, run <code>node -c controllers/[file].js</code> to ensure no syntax errors exist.",
        "<b>Step 4 — Process Restart:</b> Issue <code>pm2 restart monitoring_system</code> to reload backend services.",
        "<b>Step 5 — Incident Post-Mortem Log:</b> Document incident details, root cause, and resolution steps in Sinexus Ops Log."
    ]
    for p in playbook_steps:
        story.append(Paragraph(f"• {p}", bullet_style))
    story.append(Spacer(1, 20))

    # Sign-off box
    app_data = [
        [Paragraph("<b>MONITORING & LOGGING SPECIFICATION SIGN-OFF</b>", table_header_style), Paragraph("", table_header_style)],
        [Paragraph("<b>Ops Lead:</b> Sinexus Lead DevOps Engineer", table_cell_style), Paragraph("<b>Approved By:</b> Sinexus Chief Technology Officer", table_cell_style)],
        [Paragraph("<b>Date:</b> September 04, 2026", table_cell_style), Paragraph("<b>Status:</b> Approved for Operations Team", table_cell_style)]
    ]
    app_table = Table(app_data, colWidths=[257, 258])
    app_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(app_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Monitoring PDF successfully generated: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_pdf = "Sinexus_Edge_Monitoring_and_Logging_Guide.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
