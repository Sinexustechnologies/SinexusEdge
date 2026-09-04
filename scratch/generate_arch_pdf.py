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
            self.drawString(40, 815, "SINEXUS EDGE — SYSTEM ARCHITECTURE & DESIGN DOCUMENT")
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
        self.drawString(40, 32, "Confidential — Sinexus Edge Architecture Specification")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 32, page_str)

        self.restoreState()

def build_pdf(filename="Sinexus_Edge_Architecture_and_Design_Document.pdf"):
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
    c_secondary = colors.HexColor("#00838F")   # Teal / Cyan
    c_accent = colors.HexColor("#D84315")      # Deep Orange
    c_dark = colors.HexColor("#212121")        # Dark Neutral
    c_light_bg = colors.HexColor("#F4F6F8")    # Light Background
    c_border = colors.HexColor("#CFD8DC")      # Border Gray
    c_white = colors.HexColor("#FFFFFF")

    # Typography
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
        Paragraph("<b>SINEXUS EDGE MONITORING SYSTEM</b><br/><font size=12 color='#80DEEA'>System Architecture & Software Design Document</font>", title_style),
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
        [Paragraph("<b>System Name:</b> Sinexus Edge Monitoring Platform", body_style), Paragraph("<b>Document Version:</b> 1.0.0 (Production)", body_style)],
        [Paragraph("<b>Backend Stack:</b> Node.js, Express, MongoDB Atlas NoSQL", body_style), Paragraph("<b>Client App:</b> Synxeus Flutter Frontend App", body_style)],
        [Paragraph("<b>Target Infrastructure:</b> AWS Lightsail (Ubuntu Linux)", body_style), Paragraph("<b>Integrations:</b> Google Maps API, Firebase FCM", body_style)]
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

    # 1. System Overview & Architectural Topology
    story.append(Paragraph("1. Multi-Tier Architectural Topology", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    arch_desc = (
        "The Sinexus Edge platform follows a modern <b>4-Tier Distributed Microservices Architecture</b> designed for scalability, "
        "high availability, low latency telemetry processing, and strict multi-tenant data privacy."
    )
    story.append(Paragraph(arch_desc, body_style))
    story.append(Spacer(1, 8))

    # Tier Table
    tier_data = [
        [Paragraph("Tier Layer", table_header_style), Paragraph("Technologies Used", table_header_style), Paragraph("Architectural Purpose & Core Design Patterns", table_header_style)],
        [Paragraph("<b>1. Hardware Telemetry Tier</b>", table_cell_style), Paragraph("ESP32, Odor Sensors, Footfall Counters, Feedback Nodes", table_cell_style), Paragraph("Collects ambient sanitation data at facility level. Transmits metrics to cloud backend via HTTP/MQTT telemetry ingestion endpoints.", table_cell_style)],
        [Paragraph("<b>2. Application API Tier</b>", table_cell_style), Paragraph("Node.js v20+, Express.js, Socket.IO, JWT", table_cell_style), Paragraph("RESTful microservices, Event-driven WebSockets, Rule Classifier Engine, Rate limiting middleware, and Google Maps geocoding adapter.", table_cell_style)],
        [Paragraph("<b>3. Persistence & Audit Tier</b>", table_cell_style), Paragraph("MongoDB Atlas, Mongoose ODM", table_cell_style), Paragraph("High-throughput NoSQL cluster storing user accounts, device registry, active assignments, telemetry caches, alerts, tasks, and legal consent logs.", table_cell_style)],
        [Paragraph("<b>4. Presentation Client Tier</b>", table_cell_style), Paragraph("Flutter (Dart), Material 3 Design", table_cell_style), Paragraph("Cross-platform mobile/tablet application for Admins and Cleaning Staff. Implements declarative routing, real-time push notifications, and local state management.", table_cell_style)],
    ]
    tier_table = Table(tier_data, colWidths=[120, 120, 275])
    tier_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(tier_table)
    story.append(Spacer(1, 14))

    # 2. Software Design Patterns
    story.append(Paragraph("2. Software Design Patterns & Modular Structure", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    patterns = [
        "<b>Controller-Service-Model Pattern:</b> Separates route handlers (Controllers), domain business logic (Services like <code>alertClassifier.js</code>, <code>notificationService.js</code>, <code>ratingService.js</code>), and data access objects (Mongoose Models).",
        "<b>Middleware Pipeline Architecture:</b> Implements chained request execution for JWT token verification (<code>authMiddleware</code>), request validation (<code>express-validator</code>), rate limiting (<code>express-rate-limit</code>), and centralized error handling (<code>errorHandler</code>).",
        "<b>Singleton & Adapter Pattern:</b> External integrations (Google Maps Geocoding Service, Firebase Admin SDK instance) are wrapped as singletons to reuse connection pools and manage credentials securely.",
        "<b>Event-Driven Observer Pattern:</b> Real-time updates (e.g. <code>assignments_updated</code>) are emitted via Socket.IO WebSocket channels to keep UI clients synchronized without polling."
    ]
    for p in patterns:
        story.append(Paragraph(f"• {p}", bullet_style))
    story.append(Spacer(1, 14))

    # 3. Database Schema & Data Models
    story.append(Paragraph("3. Database Schema & Data Models Specification", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    schema_data = [
        [Paragraph("Collection / Model", table_header_style), Paragraph("Key Fields & Types", table_header_style), Paragraph("Indexes & Relational Bindings", table_header_style)],
        [Paragraph("<b>User</b>", table_cell_style), Paragraph("<code>userId</code> (String), <code>email</code> (String), <code>password</code> (Hash), <code>role</code> ('admin'/'staff'), <code>adminId</code> (ObjectId), <code>assignedDevice</code> (ObjectId), <code>fcmTokens</code> (Array)", table_cell_style), Paragraph("Unique index on <code>email</code> and <code>userId</code>. Admin ID auto-generated (<code>NAME-COMPANY</code>). Staff ID auto-generated (<code>STF001</code>).", table_cell_style)],
        [Paragraph("<b>Device</b>", table_cell_style), Paragraph("<code>device_uid</code> (String), <code>deviceId</code> (String), <code>adminId</code> (ObjectId), <code>locationName</code> (String), <code>floor</code> (String), <code>latitude</code> (Number), <code>longitude</code> (Number), <code>assignedStaff</code> (ObjectId)", table_cell_style), Paragraph("Unique index on <code>device_uid</code> and <code>deviceId</code>. Foreign key reference to Admin User and assigned Staff User.", table_cell_style)],
        [Paragraph("<b>Assignment</b>", table_cell_style), Paragraph("<code>staff</code> (ObjectId), <code>device</code> (ObjectId), <code>adminId</code> (ObjectId), <code>status</code> ('ACTIVE'/'INACTIVE'), <code>assignedAt</code> (Date), <code>unassignedAt</code> (Date)", table_cell_style), Paragraph("Compound index on <code>(device, status)</code>. Maintains audit history of staff allocations over time.", table_cell_style)],
        [Paragraph("<b>Alert</b>", table_cell_style), Paragraph("<code>device</code> (ObjectId), <code>adminId</code> (ObjectId), <code>alertType</code> ('ODOR'/'FEEDBACK'), <code>severity</code> ('MODERATE'/'URGENT'), <code>status</code> ('OPEN'/'ASSIGNED'/'RESOLVED')", table_cell_style), Paragraph("Index on <code>(status, adminId)</code>. Generated by Classifier Engine upon threshold breaches.", table_cell_style)],
        [Paragraph("<b>Task</b>", table_cell_style), Paragraph("<code>alert</code> (ObjectId), <code>device</code> (ObjectId), <code>staff</code> (ObjectId), <code>status</code> ('ASSIGNED'/'IN_PROGRESS'/'SUBMITTED'/'VERIFIED'), <code>proofPhotoUri</code> (String), <code>timeline</code> (Array)", table_cell_style), Paragraph("Index on <code>(staff, status)</code>. Contains timeline array logging status changes with timestamps.", table_cell_style)],
        [Paragraph("<b>ConsentLog</b>", table_cell_style), Paragraph("<code>userId</code> (ObjectId), <code>userType</code> ('admin'/'staff'), <code>termsVersion</code> (String), <code>ipAddress</code> (String), <code>userAgent</code> (String), <code>termsAcceptedAt</code> (Date)", table_cell_style), Paragraph("Compliance audit store recording explicit acceptance of Terms & Privacy policy.", table_cell_style)],
    ]
    schema_table = Table(schema_data, colWidths=[105, 210, 200])
    schema_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(schema_table)
    story.append(Spacer(1, 14))

    # Page Break for clean layout
    story.append(PageBreak())

    # 4. Security & Privacy Architecture
    story.append(Paragraph("4. Security & Multi-Tenancy Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    sec_items = [
        "<b>Stateless Authentication (JWT & Refresh Strategy):</b> Short-lived JWT Access Tokens (15-minute expiration) signed with <code>JWT_SECRET</code>, coupled with 7-day Refresh Tokens stored securely in MongoDB.",
        "<b>Password Security:</b> Passwords hashed using <code>bcryptjs</code> with salt round factor 10.",
        "<b>Strict Multi-Tenant Scoping:</b> All database queries for Devices, Staff, Assignments, Alerts, and Reports are strictly scoped using <code>adminId: req.user.id</code> to ensure tenant isolation.",
        "<b>Input Validation & Sanitization:</b> <code>express-validator</code> rules sanitize request parameters, preventing SQL/NoSQL injection attacks.",
        "<b>Rate Limiting & DDoS Defense:</b> <code>express-rate-limit</code> limits authentication attempts to protect against brute-force attacks.",
        "<b>Auditability & Legal Compliance:</b> Terms & Conditions and Privacy Policy acceptances are logged in an immutable <code>ConsentLog</code> table capturing user IP, User Agent, and timestamp."
    ]
    for s in sec_items:
        story.append(Paragraph(f"• {s}", bullet_style))
    story.append(Spacer(1, 14))

    # 5. Infrastructure & Deployment Topology
    story.append(Paragraph("5. Infrastructure & Deployment Topology", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    deploy_desc = (
        "The backend API server is optimized for high-performance hosting on <b>AWS Lightsail VPS</b> running Ubuntu Linux. "
        "Process management is driven by PM2 with auto-restart, cluster mode support, and log rotation."
    )
    story.append(Paragraph(deploy_desc, body_style))
    story.append(Spacer(1, 8))

    deploy_data = [
        [Paragraph("Environment Component", table_header_style), Paragraph("Specification / Service", table_header_style), Paragraph("Configuration Details", table_header_style)],
        [Paragraph("<b>Cloud Provider</b>", table_cell_style), Paragraph("AWS Lightsail VPS", table_cell_style), Paragraph("Ubuntu 22.04 LTS, Static Public IPv4, Firewall ports 80/443 enabled", table_cell_style)],
        [Paragraph("<b>Process Manager</b>", table_cell_style), Paragraph("PM2 Process Daemon", table_cell_style), Paragraph("Configured for automated startup on boot, crash recovery, and memory monitoring", table_cell_style)],
        [Paragraph("<b>Database Cluster</b>", table_cell_style), Paragraph("MongoDB Atlas", table_cell_style), Paragraph("Multi-region replica set, automated backups, TLS 1.3 encrypted connections", table_cell_style)],
        [Paragraph("<b>Push Gateway</b>", table_cell_style), Paragraph("Firebase Admin SDK", table_cell_style), Paragraph("Service Account JSON authentication for background FCM push notification delivery", table_cell_style)],
    ]
    deploy_table = Table(deploy_data, colWidths=[130, 130, 255])
    deploy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(deploy_table)
    story.append(Spacer(1, 20))

    # Sign-Off Box
    app_data = [
        [Paragraph("<b>ARCHITECTURE SPECIFICATION SIGN-OFF</b>", table_header_style), Paragraph("", table_header_style)],
        [Paragraph("<b>Architect:</b> Lead System Architect", table_cell_style), Paragraph("<b>DevOps Lead:</b> Infrastructure & Cloud Lead", table_cell_style)],
        [Paragraph("<b>Date:</b> September 04, 2026", table_cell_style), Paragraph("<b>Status:</b> Approved for Production Deployment", table_cell_style)]
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
    print(f"Architecture PDF successfully generated: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_pdf = "Sinexus_Edge_Architecture_and_Design_Document.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
