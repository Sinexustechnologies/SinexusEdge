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
            self.drawString(40, 815, "SINEXUS EDGE — MODULE-WISE FUNCTIONAL DESCRIPTION & USER MANUAL")
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
        self.drawString(40, 32, "Confidential — Operations & User Manual")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 32, page_str)

        self.restoreState()

def build_pdf(filename="Sinexus_Edge_User_Manual_and_Functional_Description.pdf"):
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
    c_accent = colors.HexColor("#2E7D32")      # Green Accent
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
        Paragraph("<b>SINEXUS EDGE MONITORING SYSTEM</b><br/><font size=12 color='#A5D6A7'>Module-wise Functional Description & User Manual</font>", title_style),
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
        [Paragraph("<b>System Name:</b> Sinexus Edge Monitoring System", body_style), Paragraph("<b>Document Type:</b> Functional Description & User Manual", body_style)],
        [Paragraph("<b>Target Apps:</b> Synxeus Frontend (Mobile/Tablet)", body_style), Paragraph("<b>Target Roles:</b> Administrator, Facility Manager, Staff", body_style)],
        [Paragraph("<b>Backend API:</b> Node.js REST API (AWS Lightsail)", body_style), Paragraph("<b>Release Version:</b> 1.0.0 (Production)", body_style)]
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

    # Introduction
    story.append(Paragraph("1. System Purpose & Target Audience", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    intro_p = (
        "This document serves as the comprehensive <b>User Manual and Module-wise Functional Specification</b> for the Sinexus Edge Monitoring System. "
        "It provides step-by-step operational instructions and functional descriptions for all core software modules, guiding Administrators, "
        "Facility Regional Managers, and Cleaning Personnel in operating the Synxeus Frontend mobile app and backend web portal efficiently."
    )
    story.append(Paragraph(intro_p, body_style))
    story.append(Spacer(1, 10))

    # Module Summary Table
    story.append(Paragraph("<b>System Modules Overview:</b>", h2_style))
    mod_summary_data = [
        [Paragraph("Module Name", table_header_style), Paragraph("Primary User Roles", table_header_style), Paragraph("Core Functional Scope", table_header_style)],
        [Paragraph("<b>1. Authentication & Onboarding</b>", table_cell_style), Paragraph("Admin, Staff", table_cell_style), Paragraph("Self-registration, Email OTP verification, Terms/Privacy consent, Auto Admin ID, Staff onboarding, Password management.", table_cell_style)],
        [Paragraph("<b>2. Facility & Device Registry</b>", table_cell_style), Paragraph("Admin", table_cell_style), Paragraph("Registering toilet nodes, hardware UID mapping, Automated Google Maps GPS geocoding, floor & location organization.", table_cell_style)],
        [Paragraph("<b>3. Staff Allocation & Assignment</b>", table_cell_style), Paragraph("Admin", table_cell_style), Paragraph("Single and bulk device-to-staff allocations, active assignment history, automated task migration upon staff reassignment.", table_cell_style)],
        [Paragraph("<b>4. Real-time Telemetry & Alerts</b>", table_cell_style), Paragraph("Admin, System", table_cell_style), Paragraph("Classifier Engine threshold processing (Odor ppm, Counter, Feedback), Moderate vs Urgent alert generation, alert feed.", table_cell_style)],
        [Paragraph("<b>5. Task Execution & Proof Upload</b>", table_cell_style), Paragraph("Cleaning Staff, Admin", table_cell_style), Paragraph("FCM push notifications, task acceptance (IN_PROGRESS), cleaning photo proof capture, submission, and Admin verification sign-off.", table_cell_style)],
        [Paragraph("<b>6. Analytics & Reports</b>", table_cell_style), Paragraph("Admin", table_cell_style), Paragraph("City overview, toilet status counts, Particular Rating algorithms (1-5 scale), historical report filters, CSV export.", table_cell_style)],
    ]
    mod_table = Table(mod_summary_data, colWidths=[130, 105, 280])
    mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(mod_table)
    story.append(Spacer(1, 14))

    # Module 1: Authentication & Onboarding
    story.append(Paragraph("Module 1: Authentication & Account Management", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    m1_desc = [
        "<b>1.1 Admin Self-Registration:</b> New Administrators open Synxeus Frontend, fill in Name, Company Name, Email Address, Mobile Number, and Password.",
        "<b>1.2 Email OTP Verification:</b> App sends a 6-digit OTP to the registered email. User inputs OTP to verify email authenticity before account creation.",
        "<b>1.3 Terms & Privacy Policy Consent:</b> User checks the mandatory T&C and Privacy Policy box. Acceptance timestamp, version, IP address, and browser User Agent are recorded in <code>ConsentLog</code> for legal compliance.",
        "<b>1.4 System Auto-Generated Admin ID:</b> Backend function <code>generateUniqueAdminId</code> generates a normalized, uppercase ID formatted as <code>NAME-COMPANY</code> (e.g. <code>RAHUL-SHARMA-SINEXUS-TECH</code>). Duplicate names receive auto-incrementing suffixes (e.g. <code>-001</code>).",
        "<b>1.5 Secure Authentication & FCM Registration:</b> Upon login, backend returns JWT Access Tokens (15-min lifespan) and Refresh Tokens (7-day lifespan). The client registers its Firebase FCM token for push alerts."
    ]
    for d in m1_desc:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 14))

    # Module 2: Facility & Device Management
    story.append(Paragraph("Module 2: Facility & Device Management", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    m2_desc = [
        "<b>2.1 Registering a Toilet Facility:</b> Admin enters Hardware UID (<code>device_uid</code>), Category (e.g. Public Toilet, Executive Restroom), Model Number, Floor, Location Name, and Address.",
        "<b>2.2 Automated GPS Geocoding:</b> If GPS coordinates are omitted, the backend invokes <code>googleMapsService.geocodeAddress</code> to automatically resolve the street address to geographical Latitude and Longitude.",
        "<b>2.3 Standardized Device ID Formatting:</b> System auto-formats Device ID as <code>[LOCATION]-[FLOOR]-[COUNT]</code> (e.g. <code>AIRPORT-F1-01</code>).",
        "<b>2.4 Facility Live Dashboard Cards:</b> Each facility is presented as a card displaying live Odor level (ppm), Footfall count, Feedback count, and current status: <font color='#2E7D32'><b>Clean</b></font>, <font color='#E65100'><b>Moderate</b></font>, or <font color='#C62828'><b>Urgent</b></font>."
    ]
    for d in m2_desc:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 14))

    # Page Break for clean layout
    story.append(PageBreak())

    # Module 3: Staff Allocation & Device Assignment
    story.append(Paragraph("Module 3: Staff Onboarding & Device Assignment", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    m3_desc = [
        "<b>3.1 Onboarding Cleaning Staff:</b> Admin registers staff members with Name, Email, Mobile, Designation, and Employee ID. System auto-generates a unique Staff ID (e.g., <code>STF001</code>). Default password is set to <code>Staff@1234</code>.",
        "<b>3.2 Device Allocation Workflow:</b> Admin selects a staff member and assigns one or multiple facility devices. Backend creates an <code>ACTIVE</code> record in <code>Assignment</code> collection and updates <code>Device.assignedStaff</code>.",
        "<b>3.3 Automated Task Reassignment:</b> If a device is reassigned from Staff A to Staff B, all open/pending tasks for that device are automatically reassigned to Staff B with an updated timeline audit log.",
        "<b>3.4 Password Reset via Email OTP:</b> Staff members can request a password reset from their app login screen. A 6-digit OTP is sent to their registered email for identity verification."
    ]
    for d in m3_desc:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 14))

    # Module 4: Real-time Telemetry & Intelligent Alerts
    story.append(Paragraph("Module 4: Real-time Telemetry & Anomaly Alert Engine", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    m4_desc = [
        "<b>4.1 Sensor Data Ingestion:</b> IoT Gateway nodes post real-time telemetry (Odor level, Usage Counter, Feedback button presses) to <code>LatestDeviceStatus</code> and <code>SensorData</code>.",
        "<b>4.2 Classifier Engine Evaluation:</b> Backend service <code>alertClassifier.js</code> compares incoming telemetry against operational thresholds.",
        "<b>4.3 Severity Categorization:</b>",
        "&nbsp;&nbsp;&nbsp;&nbsp;- <b>Moderate Alert:</b> Triggered when Odor level exceeds moderate threshold or feedback score drops.",
        "&nbsp;&nbsp;&nbsp;&nbsp;- <b>Urgent Alert:</b> Triggered when Odor level breaches critical safety threshold or multiple negative feedback hits occur.",
        "<b>4.4 Alert Feed & History:</b> Admins can filter alerts by Active, In-Progress, Resolved, and Expired states."
    ]
    for d in m4_desc:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 14))

    # Module 5: Cleaning Task Execution & Proof Upload
    story.append(Paragraph("Module 5: Task Dispatch, Cleaning Execution & Verification", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    task_table_data = [
        [Paragraph("Step / Action", table_header_style), Paragraph("Actor & System Flow", table_header_style), Paragraph("Status Update & Payload Details", table_header_style)],
        [Paragraph("<b>1. Auto Dispatch</b>", table_cell_style), Paragraph("Backend Task Service creates Task bound to assigned staff and dispatches Firebase FCM Push Notification.", table_cell_style), Paragraph("Task Created: Status <code>ASSIGNED</code>.<br/>Push Alert: 'New Urgent Task Assigned'.", table_cell_style)],
        [Paragraph("<b>2. Task Acceptance</b>", table_cell_style), Paragraph("Staff opens mobile app, views task details, and taps <b>Start Task</b>.", table_cell_style), Paragraph("Status updated to <code>IN_PROGRESS</code>.<br/>Timestamp recorded: <code>startedAt = now</code>.", table_cell_style)],
        [Paragraph("<b>3. Execution & Proof</b>", table_cell_style), Paragraph("Staff performs cleaning, opens app camera/gallery, captures proof photo, and submits task.", table_cell_style), Paragraph("Status updated to <code>SUBMITTED</code>.<br/>Payload includes <code>proofPhotoUri</code> & <code>completedAt</code>.", table_cell_style)],
        [Paragraph("<b>4. Admin Verification</b>", table_cell_style), Paragraph("Admin inspects proof photo on dashboard and taps <b>Verify Task</b>.", table_cell_style), Paragraph("Task status updated to <code>VERIFIED</code>.<br/>Corresponding Alert marked <code>RESOLVED</code>.", table_cell_style)],
    ]
    task_table = Table(task_table_data, colWidths=[110, 215, 190])
    task_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(task_table)
    story.append(Spacer(1, 14))

    # Module 6: Analytics & Reports
    story.append(Paragraph("Module 6: Reports, Ratings & Analytics Module", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    m6_desc = [
        "<b>6.1 City Overview & Facility Summary:</b> Dashboard displays aggregate counts of total facilities, clean toilets, moderate alerts, urgent alerts, and active cleaning staff.",
        "<b>6.2 Particular Rating Score (1-5 Star Scale):</b> Backend service <code>ratingService.js</code> calculates a dynamic rating score for each facility based on average Odor levels, Feedback ratings, and cleaning turnaround times.",
        "<b>6.3 CSV Data Export:</b> Admins can export historical telemetry logs, task completion reports, and staff efficiency metrics to CSV files for management audits."
    ]
    for d in m6_desc:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 20))

    # Sign-off box
    app_data = [
        [Paragraph("<b>USER MANUAL & FUNCTIONAL SPECIFICATION APPROVAL</b>", table_header_style), Paragraph("", table_header_style)],
        [Paragraph("<b>Author:</b> Product Engineering Lead", table_cell_style), Paragraph("<b>QA Lead:</b> Quality Assurance & Delivery Lead", table_cell_style)],
        [Paragraph("<b>Date:</b> September 04, 2026", table_cell_style), Paragraph("<b>Status:</b> Approved for Client Delivery", table_cell_style)]
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

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"User Manual PDF successfully generated: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_pdf = "Sinexus_Edge_User_Manual_and_Functional_Description.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
