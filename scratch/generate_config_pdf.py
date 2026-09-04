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
            self.drawString(40, 815, "SINEXUS EDGE — SYSTEM CONFIGURATION & ENVIRONMENT GUIDE")
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
        self.drawString(40, 32, "Confidential — System Configuration & Operations Guide")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 32, page_str)

        self.restoreState()

def build_pdf(filename="Sinexus_Edge_Configuration_Details_Document.pdf"):
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
    c_accent = colors.HexColor("#00695C")      # Dark Teal Accent
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
        Paragraph("<b>SINEXUS EDGE MONITORING SYSTEM</b><br/><font size=12 color='#B2DFDB'>System Configuration Details & Deployment Guide</font>", title_style),
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
        [Paragraph("<b>System Name:</b> Sinexus Edge Monitoring Platform", body_style), Paragraph("<b>Document Type:</b> Configuration & Environment Guide", body_style)],
        [Paragraph("<b>Backend Environment:</b> AWS Lightsail (Node.js v20 LTS)", body_style), Paragraph("<b>Database:</b> MongoDB Atlas Cluster", body_style)],
        [Paragraph("<b>Process Manager:</b> PM2 Runtime Daemon", body_style), Paragraph("<b>Document Version:</b> 1.0.0 (Production)", body_style)]
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

    # 1. Executive Overview & Environment Architecture
    story.append(Paragraph("1. System Configuration Overview", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    exec_p = (
        "The <b>Configuration Details Document</b> outlines all system environment variables, database cluster settings, third-party API credentials, "
        "hardware sensor classifier parameters, and process manager configurations required to deploy and maintain the Sinexus Edge platform in production."
    )
    story.append(Paragraph(exec_p, body_style))
    story.append(Spacer(1, 10))

    # 2. Environment Variables Reference Table (.env)
    story.append(Paragraph("2. Environment Variables Reference Guide (.env)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    env_data = [
        [Paragraph("Variable Name", table_header_style), Paragraph("Purpose / Description", table_header_style), Paragraph("Example Value / Fallback", table_header_style), Paragraph("Security", table_header_style)],
        [Paragraph("<code>PORT</code>", table_cell_style), Paragraph("HTTP port on which backend Express server listens.", table_cell_style), Paragraph("<code>5000</code>", table_cell_style), Paragraph("Standard", table_cell_style)],
        [Paragraph("<code>NODE_ENV</code>", table_cell_style), Paragraph("Application runtime environment mode.", table_cell_style), Paragraph("<code>production</code>", table_cell_style), Paragraph("Standard", table_cell_style)],
        [Paragraph("<code>MONGO_URI</code>", table_cell_style), Paragraph("MongoDB Atlas connection string with TLS parameters.", table_cell_style), Paragraph("<code>mongodb+srv://user:pass@cluster.mongodb.net/dbname</code>", table_cell_style), Paragraph("<font color='#C62828'><b>CRITICAL</b></font>", table_cell_style)],
        [Paragraph("<code>JWT_SECRET</code>", table_cell_style), Paragraph("Secret key for signing 15-minute JWT Access Tokens.", table_cell_style), Paragraph("<code>super_secret_jwt_key_2026</code>", table_cell_style), Paragraph("<font color='#C62828'><b>HIGH</b></font>", table_cell_style)],
        [Paragraph("<code>JWT_REFRESH_SECRET</code>", table_cell_style), Paragraph("Secret key for signing 7-day JWT Refresh Tokens.", table_cell_style), Paragraph("<code>super_secret_refresh_key_2026</code>", table_cell_style), Paragraph("<font color='#C62828'><b>HIGH</b></font>", table_cell_style)],
        [Paragraph("<code>CURRENT_TERMS_VERSION</code>", table_cell_style), Paragraph("Legal Terms & Privacy Policy active version string.", table_cell_style), Paragraph("<code>1.0</code>", table_cell_style), Paragraph("Standard", table_cell_style)],
        [Paragraph("<code>GOOGLE_MAPS_API_KEY</code>", table_cell_style), Paragraph("Server-side Google Maps Geocoding API key.", table_cell_style), Paragraph("<code>AIzaSyD-ExampleKeyString...</code>", table_cell_style), Paragraph("<font color='#E65100'><b>MEDIUM</b></font>", table_cell_style)],
        [Paragraph("<code>FIREBASE_SERVICE_ACCOUNT</code>", table_cell_style), Paragraph("Path to Firebase Admin Service Account JSON for FCM.", table_cell_style), Paragraph("<code>./config/firebase-service-account.json</code>", table_cell_style), Paragraph("<font color='#C62828'><b>HIGH</b></font>", table_cell_style)],
        [Paragraph("<code>EMAIL_HOST</code>", table_cell_style), Paragraph("SMTP Server hostname for OTP email delivery.", table_cell_style), Paragraph("<code>smtp.gmail.com</code>", table_cell_style), Paragraph("Standard", table_cell_style)],
        [Paragraph("<code>EMAIL_USER</code>", table_cell_style), Paragraph("SMTP authentication email username.", table_cell_style), Paragraph("<code>alerts@sinexusedge.com</code>", table_cell_style), Paragraph("<font color='#E65100'><b>MEDIUM</b></font>", table_cell_style)],
        [Paragraph("<code>EMAIL_PASS</code>", table_cell_style), Paragraph("SMTP authentication password / app password.", table_cell_style), Paragraph("<code>xxxx-xxxx-xxxx-xxxx</code>", table_cell_style), Paragraph("<font color='#C62828'><b>HIGH</b></font>", table_cell_style)],
    ]
    env_table = Table(env_data, colWidths=[130, 160, 155, 70])
    env_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 4.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(env_table)
    story.append(Spacer(1, 14))

    # Page Break for clean layout
    story.append(PageBreak())

    # 3. Database Cluster Configuration
    story.append(Paragraph("3. Database Cluster & Connection Pool Configuration", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    db_details = [
        "<b>Mongoose Connection Pool Settings:</b> <code>maxPoolSize: 10</code>, <code>serverSelectionTimeoutMS: 5000</code>, <code>socketTimeoutMS: 45000</code>.",
        "<b>TLS / SSL Encryption:</b> Mandatory TLS 1.3 encrypted transport enforced by MongoDB Atlas cluster.",
        "<b>Automatic Schema Indexing:</b> Unique index constraints automatically built on startup for <code>User.email</code>, <code>User.userId</code>, <code>Device.device_uid</code>, and <code>Device.deviceId</code>.",
        "<b>Data Expiration (TTL Indexes):</b> OTP records in <code>Otp</code> collection auto-deleted after 10 minutes via <code>expiresAt</code> index."
    ]
    for d in db_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 14))

    # 4. IoT Sensor Thresholds & Classifier Config
    story.append(Paragraph("4. IoT Telemetry Thresholds & Classifier Configuration", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    thresh_data = [
        [Paragraph("Metric / Sensor", table_header_style), Paragraph("Clean Range", table_header_style), Paragraph("Moderate Alert Range", table_header_style), Paragraph("Urgent Alert Range", table_header_style)],
        [Paragraph("<b>Odor Sensor (ppm)</b>", table_cell_style), Paragraph("0 – 299 ppm", table_cell_style), Paragraph("300 – 599 ppm", table_cell_style), Paragraph("≥ 600 ppm", table_cell_style)],
        [Paragraph("<b>Footfall Counter</b>", table_cell_style), Paragraph("< 50 visits", table_cell_style), Paragraph("50 – 99 visits", table_cell_style), Paragraph("≥ 100 visits", table_cell_style)],
        [Paragraph("<b>User Feedback</b>", table_cell_style), Paragraph("GREAT / GOOD", table_cell_style), Paragraph("OK", table_cell_style), Paragraph("POOR", table_cell_style)],
    ]
    thresh_table = Table(thresh_data, colWidths=[120, 125, 135, 135])
    thresh_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(thresh_table)
    story.append(Spacer(1, 14))

    # 5. AWS Lightsail & PM2 Runtime Config
    story.append(Paragraph("5. AWS Lightsail & PM2 Process Daemon Configuration", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    pm2_desc = [
        "<b>Node.js Runtime:</b> Node.js v20.x LTS installed on Ubuntu 22.04 LTS VPS.",
        "<b>PM2 Command & Auto-Start:</b> Server process managed via PM2 (<code>pm2 start index.js --name monitoring_system</code>). Startup script enabled via <code>pm2 startup</code> and saved via <code>pm2 save</code>.",
        "<b>Restart Strategy:</b> Configured to automatically restart process on unhandled crashes or if memory usage exceeds 500 MB."
    ]
    for p in pm2_desc:
        story.append(Paragraph(f"• {p}", bullet_style))
    story.append(Spacer(1, 20))

    # Sign-off box
    app_data = [
        [Paragraph("<b>CONFIGURATION SPECIFICATION SIGN-OFF</b>", table_header_style), Paragraph("", table_header_style)],
        [Paragraph("<b>DevOps Lead:</b> Infrastructure & Cloud Engineer", table_cell_style), Paragraph("<b>Approved By:</b> Sinexus Lead Architect", table_cell_style)],
        [Paragraph("<b>Date:</b> September 04, 2026", table_cell_style), Paragraph("<b>Status:</b> Verified & Deployed to Production", table_cell_style)]
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
    print(f"Configuration PDF successfully generated: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_pdf = "Sinexus_Edge_Configuration_Details_Document.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
