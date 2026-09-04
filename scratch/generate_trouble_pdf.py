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
            self.drawString(40, 815, "SINEXUS EDGE — SYSTEM TROUBLESHOOTING & MAINTENANCE GUIDE")
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
        self.drawString(40, 32, "Confidential — System Troubleshooting & Operations Guide")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 32, page_str)

        self.restoreState()

def build_pdf(filename="Sinexus_Edge_Troubleshooting_Guide.pdf"):
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
    c_accent = colors.HexColor("#B71C1C")      # Dark Red Accent
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
        Paragraph("<b>SINEXUS EDGE MONITORING SYSTEM</b><br/><font size=12 color='#FFCDD2'>System Troubleshooting & Maintenance Guide</font>", title_style),
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
        [Paragraph("<b>System Name:</b> Sinexus Edge Monitoring Platform", body_style), Paragraph("<b>Document Type:</b> System Troubleshooting & Ops Guide", body_style)],
        [Paragraph("<b>Backend API:</b> Node.js, Express, MongoDB Atlas", body_style), Paragraph("<b>Target Roles:</b> Support Engineers, Systems Admins", body_style)],
        [Paragraph("<b>Platform:</b> AWS Lightsail (PM2 Process Daemon)", body_style), Paragraph("<b>Document Version:</b> 1.0.0 (Production)", body_style)]
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

    # 1. Executive Summary & Diagnostic Approach
    story.append(Paragraph("1. Executive Summary & Diagnostic Methodology", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    exec_p = (
        "The <b>Troubleshooting & Maintenance Guide</b> provides standard operating procedures, failure diagnostic trees, and resolution workflows "
        "for resolving operational anomalies across authentication, multi-tenancy scoping, IoT telemetry, push notifications, geocoding, and server infrastructure."
    )
    story.append(Paragraph(exec_p, body_style))
    story.append(Spacer(1, 10))

    # 2. Failure Diagnostic Matrix
    story.append(Paragraph("2. Categorized System Failure Matrix", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    diag_data = [
        [Paragraph("Symptom / Error Message", table_header_style), Paragraph("Probable Root Cause", table_header_style), Paragraph("Diagnostic Check & Resolution Workflow", table_header_style)],
        [Paragraph("<b><code>Validation Error</code></b> on Admin Register", table_cell_style), Paragraph("<code>userId</code> was required by validator middleware, but frontend omitted it (expecting backend auto-generation).", table_cell_style), Paragraph("Updated <code>validators.js</code> to mark <code>userId</code> as <code>.optional()</code>. Ensure frontend sends valid email, mobile, and password.", table_cell_style)],
        [Paragraph("<b><code>acceptedAt is not defined</code></b> (500 Error)", table_cell_style), Paragraph("Variable <code>acceptedAt</code> was used in <code>User.create</code> inside <code>staffController.js</code> without prior declaration.", table_cell_style), Paragraph("Declared <code>const acceptedAt = new Date()</code> in <code>staffController.js</code> before user creation call.", table_cell_style)],
        [Paragraph("<b>New Admin sees Old Devices & Staff</b>", table_cell_style), Paragraph("Legacy fallback code triggered <code>Device.find()</code> / <code>User.find()</code> when an admin had 0 devices/staff, leaking other accounts' data.", table_cell_style), Paragraph("Removed global fallbacks in <code>staffController.js</code> & <code>assignmentController.js</code>. Restart PM2 on Lightsail to flush active memory.", table_cell_style)],
        [Paragraph("<b>Staff Not Receiving Push Notifications</b>", table_cell_style), Paragraph("FCM Token not bound to staff account, or Firebase Admin Service Account credentials missing/expired.", table_cell_style), Paragraph("Inspect <code>User.fcmTokens</code> array. Verify <code>firebase-service-account.json</code> file exists and path is set in <code>.env</code>.", table_cell_style)],
        [Paragraph("<b>Location Geocoding Returns 404 / Failed</b>", table_cell_style), Paragraph("Google Maps API Key missing or IP address restricted; or street address string unresolvable.", table_cell_style), Paragraph("Check <code>GOOGLE_MAPS_API_KEY</code> in <code>.env</code>. System falls back gracefully to saving location name without blocking.", table_cell_style)],
        [Paragraph("<b>MongoDB Connection Timeout / Error</b>", table_cell_style), Paragraph("Database URI credentials invalid or IP whitelist blocked on MongoDB Atlas cluster.", table_cell_style), Paragraph("Verify <code>MONGO_URI</code> in <code>.env</code>. Ensure AWS Lightsail static IP is added to MongoDB Atlas Network Access IP Whitelist.", table_cell_style)],
    ]
    diag_table = Table(diag_data, colWidths=[130, 155, 230])
    diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 14))

    # Page Break for clean layout
    story.append(PageBreak())

    # 3. Operational Troubleshooting Procedures
    story.append(Paragraph("3. Step-by-Step Operational Workflows", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("Procedure 3.1: Log Extraction & Diagnostic Commands", h2_style))
    p1 = [
        "<b>1. View PM2 Process Status:</b> Run <code>pm2 status</code> on AWS Lightsail terminal to verify node process state.",
        "<b>2. View Live Logs:</b> Run <code>pm2 logs monitoring_system --lines 100</code> to extract real-time application output and stack traces.",
        "<b>3. Syntax Verification:</b> Validate JS syntax before restarting: <code>node -c controllers/staffController.js</code>.",
        "<b>4. Graceful Restart:</b> Restart backend service after code deployments: <code>pm2 restart monitoring_system</code>."
    ]
    for step in p1:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Procedure 3.2: Multi-Tenancy Data Leakage Resolution", h2_style))
    p2 = [
        "<b>1. Identify Scoping Violation:</b> If a new admin account retrieves devices or staff belonging to another tenant, inspect the corresponding controller query.",
        "<b>2. Verify Mandatory Scoping:</b> Ensure database queries strictly include <code>adminId: req.user.id</code>.",
        "<b>3. Remove Global Fallbacks:</b> Verify that <code>if (myDevices.length === 0)</code> does NOT invoke an un-scoped <code>Device.find()</code>.",
        "<b>4. Redeploy & Flush Cache:</b> Commit changes, pull to AWS Lightsail server, and run <code>pm2 restart all</code>."
    ]
    for step in p2:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Spacer(1, 14))

    # 4. Maintenance & Health Checks
    story.append(Paragraph("4. Server Health Check & Maintenance Commands", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    health_data = [
        [Paragraph("Health / Audit Task", table_header_style), Paragraph("Terminal Command / Check", table_header_style), Paragraph("Expected Healthy Output", table_header_style)],
        [Paragraph("<b>PM2 Process Status</b>", table_cell_style), Paragraph("<code>pm2 status</code>", table_cell_style), Paragraph("Status: <code>online</code>, Restarts: low", table_cell_style)],
        [Paragraph("<b>Real-time Error Logs</b>", table_cell_style), Paragraph("<code>pm2 logs --err --lines 50</code>", table_cell_style), Paragraph("No unhandled exceptions or connection errors", table_cell_style)],
        [Paragraph("<b>Memory & CPU Usage</b>", table_cell_style), Paragraph("<code>pm2 monit</code> or <code>htop</code>", table_cell_style), Paragraph("Memory < 300 MB, CPU < 25%", table_cell_style)],
        [Paragraph("<b>Disk Space Audit</b>", table_cell_style), Paragraph("<code>df -h</code>", table_cell_style), Paragraph("Disk usage < 80%", table_cell_style)],
    ]
    health_table = Table(health_data, colWidths=[120, 185, 210])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(health_table)
    story.append(Spacer(1, 20))

    # Sign-off box
    app_data = [
        [Paragraph("<b>TROUBLESHOOTING GUIDE APPROVAL</b>", table_header_style), Paragraph("", table_header_style)],
        [Paragraph("<b>Support Lead:</b> Senior DevOps Support Engineer", table_cell_style), Paragraph("<b>Approved By:</b> Sinexus Lead Architect", table_cell_style)],
        [Paragraph("<b>Date:</b> September 04, 2026", table_cell_style), Paragraph("<b>Status:</b> Approved & Verified for Ops Team", table_cell_style)]
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
    print(f"Troubleshooting PDF successfully generated: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_pdf = "Sinexus_Edge_Troubleshooting_Guide.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
