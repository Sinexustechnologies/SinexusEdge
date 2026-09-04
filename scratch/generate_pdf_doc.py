import os
import sys
from reportlab.lib.pagesizes import letter, A4
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
        
        # Primary palette
        brand_blue = colors.HexColor("#0D47A1")
        text_gray = colors.HexColor("#666666")
        light_border = colors.HexColor("#E0E0E0")

        # Top Header (Only pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(brand_blue)
            self.drawString(40, 815, "SINEXUS EDGE — APPLICATION & PROCESS FLOW DOCUMENTATION")
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
        self.drawString(40, 32, "Confidential — Sinexus Edge Monitoring System")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 32, page_str)

        self.restoreState()

def build_pdf(filename="Sinexus_Edge_Application_Flow_Documentation.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    c_primary = colors.HexColor("#0D47A1")     # Deep Blue
    c_secondary = colors.HexColor("#00838F")   # Teal
    c_accent = colors.HexColor("#E65100")      # Amber/Orange
    c_dark = colors.HexColor("#212121")        # Dark Neutral
    c_light_bg = colors.HexColor("#F4F6F8")    # Light Neutral Background
    c_border = colors.HexColor("#CFD8DC")      # Border Gray
    c_white = colors.HexColor("#FFFFFF")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
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
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1A237E")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
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
        Paragraph("<b>SINEXUS EDGE MONITORING SYSTEM</b><br/><font size=13 color='#00838F'>Application & Process Flow Documentation</font>", ParagraphStyle('BannerText', parent=title_style, textColor=c_white, fontSize=20, leading=24)),
    ]]
    banner_table = Table(banner_data, colWidths=[515])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_primary),
        ('PADDING', (0, 0), (-1, -1), 16),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))

    # Metadata Card
    meta_data = [
        [Paragraph("<b>Project:</b> Sinexus Edge IoT Toilet Monitoring System", body_style), Paragraph("<b>Version:</b> 1.0.0 (Production)", body_style)],
        [Paragraph("<b>Backend Stack:</b> Node.js, Express, MongoDB Atlas, Socket.IO", body_style), Paragraph("<b>Frontend Stack:</b> Flutter (Mobile & Tablet App)", body_style)],
        [Paragraph("<b>Cloud Platform:</b> AWS Lightsail, Firebase FCM, Google Maps API", body_style), Paragraph("<b>Document Type:</b> Application & Process Flow", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[257, 258])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary & System Overview", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    exec_summary = (
        "The <b>Sinexus Edge Monitoring System</b> is an end-to-end IoT-driven sanitation monitoring and automated task management platform. "
        "It integrates hardware telemetry sensors (odor level, footfall counter, user feedback buttons) with a high-performance Node.js REST API backend "
        "and an intuitive cross-platform Flutter application (Synxeus Frontend). "
        "The platform guarantees real-time alert generation, automated cleaning task dispatch, geo-location mapping, and transparent audit trails for administrators and cleaning personnel."
    )
    story.append(Paragraph(exec_summary, body_style))
    story.append(Spacer(1, 10))

    # Component Table
    story.append(Paragraph("<b>Core Architecture Components:</b>", h2_style))
    comp_data = [
        [Paragraph("Component", table_header_style), Paragraph("Technology Stack", table_header_style), Paragraph("Role & Key Responsibilities", table_header_style)],
        [Paragraph("<b>Frontend App</b>", table_cell_style), Paragraph("Flutter (Dart)", table_cell_style), Paragraph("Cross-platform mobile/tablet application for Admins and Cleaning Staff. Handles OTP verification, dashboard visualization, real-time alerts, and task execution.", table_cell_style)],
        [Paragraph("<b>Backend API Server</b>", table_cell_style), Paragraph("Node.js, Express.js", table_cell_style), Paragraph("RESTful microservices handling Auth, RBAC, Device management, Alert classification engine, Geocoding, and Task orchestration.", table_cell_style)],
        [Paragraph("<b>Database Layer</b>", table_cell_style), Paragraph("MongoDB Atlas", table_cell_style), Paragraph("Primary NoSQL datastore storing User credentials, Device registry, Telemetry logs, Active assignments, Alerts, and Consent logs.", table_cell_style)],
        [Paragraph("<b>IoT Telemetry Gateways</b>", table_cell_style), Paragraph("MQTT / HTTP Telemetry", table_cell_style), Paragraph("Real-time sensor nodes installed at toilet facilities transmitting Odor ppm, Counter metrics, and Feedback button presses.", table_cell_style)],
        [Paragraph("<b>Push Notifications</b>", table_cell_style), Paragraph("Firebase FCM", table_cell_style), Paragraph("Delivers immediate push notifications to assigned staff members when urgent cleaning tasks are triggered.", table_cell_style)],
        [Paragraph("<b>Location Services</b>", table_cell_style), Paragraph("Google Maps Platform API", table_cell_style), Paragraph("Automatic geocoding and reverse-geocoding of facility addresses to geographical coordinates (lat/lng).", table_cell_style)],
    ]
    comp_table = Table(comp_data, colWidths=[110, 115, 290])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 15))

    # 2. System User Personas
    story.append(Paragraph("2. User Roles & RBAC Matrix", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    rbac_data = [
        [Paragraph("Role", table_header_style), Paragraph("Primary Responsibilities", table_header_style), Paragraph("System Access & Permissions", table_header_style)],
        [Paragraph("<b>Administrator (Admin)</b>", table_cell_style), Paragraph("Facility oversight, staff onboarding, device registration, device-to-staff assignment, alert monitoring, task verification.", table_cell_style), Paragraph("Full tenant administrative rights. Auto-generated Admin ID (e.g. <code>NAME-COMPANY</code>). Access to executive dashboards and reports.", table_cell_style)],
        [Paragraph("<b>Cleaning Staff</b>", table_cell_style), Paragraph("Executing cleaning tasks, updating task status in real time, uploading proof of work photos upon completion.", table_cell_style), Paragraph("Restricted staff portal. Auto-assigned Staff ID (e.g. <code>STF001</code>). Receives FCM push notifications for assigned devices.", table_cell_style)],
        [Paragraph("<b>IoT Sensor Gateway</b>", table_cell_style), Paragraph("Continuously reporting ambient odor (ppm), footfall counts, and feedback button triggers.", table_cell_style), Paragraph("Automated device authentication via <code>device_uid</code>. Telemetry ingestion endpoint access.", table_cell_style)],
    ]
    rbac_table = Table(rbac_data, colWidths=[120, 195, 200])
    rbac_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(rbac_table)
    story.append(Spacer(1, 15))

    # 3. Detailed Process Flows
    story.append(Paragraph("3. Core Application Process Flows", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    # Flow 1
    story.append(Paragraph("Flow 1: Admin Registration & Authentication Workflow", h2_style))
    flow1_steps = [
        "<b>Step 1 — Admin Details Submission:</b> User inputs Name, Company Name, Contact Person, Email, Mobile, and Password in Synxeus Frontend.",
        "<b>Step 2 — Email OTP Verification:</b> App calls <code>/api/auth/send-otp</code>. Backend dispatches 6-digit OTP to admin email. Admin verifies OTP via <code>/api/auth/verify-otp</code>.",
        "<b>Step 3 — Legal Terms & Policy Acceptance:</b> User explicitly accepts Terms & Conditions and Privacy Policy (recorded in <code>ConsentLog</code> with IP and User Agent).",
        "<b>Step 4 — Auto-Generation of Admin ID:</b> Backend function <code>generateUniqueAdminId(name, company)</code> generates normalized unique Admin ID (e.g., <code>JOHN-DOE-ACME-CORP</code>).",
        "<b>Step 5 — JWT Session Token Issue:</b> Upon login validation, backend issues a 15-minute JWT Access Token and 7-day Refresh Token, plus registers device FCM Token for notifications."
    ]
    for step in flow1_steps:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Spacer(1, 10))

    # Flow 1 Visual Diagram Box
    flow1_box_data = [
        [Paragraph("<b>ADMIN AUTHENTICATION SEQUENCE</b>", ParagraphStyle('BoxHeader', parent=table_header_style, fontSize=8.5))],
        [Paragraph("<code>[Frontend] Input Form --> [POST /send-otp] --> [Email Service] Dispatch OTP<br/>[Frontend] Enter OTP --> [POST /verify-otp] --> [MongoDB] Mark OTP Verified<br/>[Frontend] Submit Register --> [POST /register-admin] --> Auto-Generate Admin ID --> Create User & Consent Log<br/>[Frontend] Submit Login --> [POST /login] --> Generate JWT Tokens & Store FCM Token --> [Dashboard]</code>", code_style)]
    ]
    flow1_box = Table(flow1_box_data, colWidths=[515])
    flow1_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BACKGROUND', (0, 1), (-1, 1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 0.5, c_primary),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(flow1_box)
    story.append(Spacer(1, 15))

    # Flow 2
    story.append(Paragraph("Flow 2: Device Registration & Geocoding Workflow", h2_style))
    flow2_steps = [
        "<b>Step 1 — Input Facility Metadata:</b> Admin enters Device Hardware UID (<code>device_uid</code>), Category, Model, Location Name, Floor, and Address.",
        "<b>Step 2 — Google Maps Geocoding:</b> If latitude/longitude are omitted, backend calls <code>googleMapsService.geocodeAddress(address)</code> to automatically fetch exact GPS coordinates.",
        "<b>Step 3 — Device ID Formatting:</b> System auto-formats Device ID as <code>[LOCATION]-[FLOOR]-[COUNT]</code> (e.g. <code>MALL-F1-01</code>).",
        "<b>Step 4 — Tenant Binding:</b> Device is securely bound to the logged-in Admin's ID (<code>adminId: req.user.id</code>)."
    ]
    for step in flow2_steps:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Spacer(1, 10))

    # Flow 3
    story.append(Paragraph("Flow 3: Staff Management & Device Assignment Workflow", h2_style))
    flow3_steps = [
        "<b>Step 1 — Staff Onboarding:</b> Admin registers cleaning staff with Name, Email, Mobile, and Employee ID (auto-assigned System ID <code>STF001</code>).",
        "<b>Step 2 — Device Allocation:</b> Admin selects staff member and assigns one or multiple facility devices via <code>/api/assignments/assign</code>.",
        "<b>Step 3 — Assignment Lifecycle:</b> System marks previous assignments as <code>INACTIVE</code> and creates a new <code>ACTIVE</code> assignment record bound to the staff member.",
        "<b>Step 4 — Automated Task Migration:</b> If a device is reassigned to a new staff member, all open/pending cleaning tasks for that device are automatically reassigned to the new staff member with a complete timeline audit trail."
    ]
    for step in flow3_steps:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Spacer(1, 10))

    # Flow 3 Diagram Box
    flow3_box_data = [
        [Paragraph("<b>DEVICE & STAFF ASSIGNMENT SEQUENCE</b>", ParagraphStyle('BoxHeader', parent=table_header_style, fontSize=8.5))],
        [Paragraph("<code>[Admin App] Select Staff + Select Device(s) --> [POST /api/assignments/assign]<br/>[Backend] 1. Deactivate existing active Assignment records (status: INACTIVE)<br/>[Backend] 2. Create new ACTIVE Assignment (staff: staff_id, device: device_id, adminId: admin_id)<br/>[Backend] 3. Update Device.assignedStaff pointer<br/>[Backend] 4. Migrate open tasks to new staff & broadcast Socket.IO 'assignments_updated' event</code>", code_style)]
    ]
    flow3_box = Table(flow3_box_data, colWidths=[515])
    flow3_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BACKGROUND', (0, 1), (-1, 1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 0.5, c_secondary),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(flow3_box)
    story.append(Spacer(1, 15))

    # Page Break for clean sectioning
    story.append(PageBreak())

    # Flow 4 & 5
    story.append(Paragraph("Flow 4: IoT Telemetry Ingestion & Intelligent Alert Lifecycle", h2_style))
    flow4_steps = [
        "<b>Step 1 — Telemetry Ingestion:</b> IoT Sensors post Odor (ppm), Counter, and Feedback telemetry to backend.",
        "<b>Step 2 — Classifier Engine:</b> <code>alertClassifier.js</code> evaluates metrics against defined operational thresholds.",
        "<b>Step 3 — Alert Triggering:</b> If Odor > threshold or Negative Feedback is logged, an Alert is generated (Severity: <code>MODERATE</code> or <code>URGENT</code>).",
        "<b>Step 4 — Alert Lifecycle States:</b> <code>OPEN</code> (Generated) --> <code>ASSIGNED</code> (Assigned to Staff Task) --> <code>IN_PROGRESS</code> (Staff started cleaning) --> <code>SUBMITTED</code> (Staff uploaded proof photo) --> <code>VERIFIED / RESOLVED</code> (Admin approved)."
    ]
    for step in flow4_steps:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Flow 5: Staff Cleaning Task Execution & Verification Workflow", h2_style))
    flow5_steps = [
        "<b>Step 1 — Automatic Task Dispatch:</b> When an alert is created, backend creates a <code>Task</code> bound to the device's assigned staff and sends an instant Firebase FCM Push Notification.",
        "<b>Step 2 — Task Acceptance & Start:</b> Staff opens mobile app, views assigned task, and taps <b>Start Task</b> (updates status to <code>IN_PROGRESS</code> with timestamp).",
        "<b>Step 3 — Work Execution & Proof Upload:</b> After cleaning, staff takes/uploads a proof photo (verified with camera/gallery permission check) and submits task (updates status to <code>SUBMITTED</code>).",
        "<b>Step 4 — Admin Review & Resolution:</b> Admin inspects submission on dashboard and marks task as <code>VERIFIED/RESOLVED</code>. The corresponding Alert is automatically marked <code>RESOLVED</code>."
    ]
    for step in flow5_steps:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Spacer(1, 10))

    # Flow 4 & 5 Combined Matrix Table
    story.append(Paragraph("<b>Alert & Task Lifecycle State Matrix:</b>", h2_style))
    matrix_data = [
        [Paragraph("Alert State", table_header_style), Paragraph("Task State", table_header_style), Paragraph("Trigger / Action Taken", table_header_style), Paragraph("Actor", table_header_style)],
        [Paragraph("<code>OPEN</code>", table_cell_style), Paragraph("<code>PENDING</code>", table_cell_style), Paragraph("Odor / Feedback threshold exceeded by IoT sensor", table_cell_style), Paragraph("Classifier Engine", table_cell_style)],
        [Paragraph("<code>ASSIGNED</code>", table_cell_style), Paragraph("<code>ASSIGNED</code>", table_cell_style), Paragraph("Task automatically created & FCM push notification sent", table_cell_style), Paragraph("Backend Task Service", table_cell_style)],
        [Paragraph("<code>ASSIGNED</code>", table_cell_style), Paragraph("<code>IN_PROGRESS</code>", table_cell_style), Paragraph("Staff taps 'Start Task' in mobile app", table_cell_style), Paragraph("Cleaning Staff", table_cell_style)],
        [Paragraph("<code>ASSIGNED</code>", table_cell_style), Paragraph("<code>SUBMITTED</code>", table_cell_style), Paragraph("Staff uploads proof of work photo & submits task", table_cell_style), Paragraph("Cleaning Staff", table_cell_style)],
        [Paragraph("<code>RESOLVED</code>", table_cell_style), Paragraph("<code>VERIFIED</code>", table_cell_style), Paragraph("Admin reviews proof photo & approves resolution", table_cell_style), Paragraph("Administrator", table_cell_style)],
    ]
    matrix_table = Table(matrix_data, colWidths=[90, 95, 230, 100])
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(matrix_table)
    story.append(Spacer(1, 15))

    # 4. Database ER & Entity Relationships
    story.append(Paragraph("4. Data Model & Entity Relationships", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    er_summary = (
        "The system database is structured around clear relational bindings to guarantee multi-tenant data isolation and complete auditing:"
    )
    story.append(Paragraph(er_summary, body_style))
    story.append(Spacer(1, 6))

    er_bullets = [
        "<b>User (Admin & Staff):</b> Admin users own <code>Device</code> records via <code>adminId</code>. Staff users reference their parent admin via <code>adminId</code> and assigned device via <code>assignedDevice</code>.",
        "<b>Device:</b> Represents a physical toilet facility node. Holds <code>adminId</code>, <code>assignedStaff</code> pointer, location coordinates (lat/lng), and device model metadata.",
        "<b>Assignment:</b> Audit table logging device-to-staff allocations over time with <code>ACTIVE</code> / <code>INACTIVE</code> status flags and timestamps.",
        "<b>LatestDeviceStatus:</b> Real-time cache holding the latest telemetry readings (Odor, Counter, Feedback) per device for rapid dashboard rendering.",
        "<b>Alert & Task:</b> Alert tracks anomaly events; Task manages staff workflow, timestamps (<code>startedAt</code>, <code>completedAt</code>, <code>verifiedAt</code>), and proof image URIs.",
        "<b>ConsentLog:</b> Compliance audit table capturing terms version, acceptance timestamp, IP address, and user agent."
    ]
    for b in er_bullets:
        story.append(Paragraph(f"• {b}", bullet_style))
    story.append(Spacer(1, 15))

    # Document Footer / Approval Box
    app_data = [
        [Paragraph("<b>DOCUMENT APPROVAL & SIGN-OFF</b>", table_header_style), Paragraph("", table_header_style)],
        [Paragraph("<b>Prepared By:</b> Antigravity Engineering Team", table_cell_style), Paragraph("<b>Approved By:</b> Sinexus Lead Architect", table_cell_style)],
        [Paragraph("<b>Date:</b> September 04, 2026", table_cell_style), Paragraph("<b>Status:</b> Approved for Delivery", table_cell_style)]
    ]
    app_table = Table(app_data, colWidths=[257, 258])
    app_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(app_table)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Successfully generated: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_pdf = "Sinexus_Edge_Application_Flow_Documentation.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
