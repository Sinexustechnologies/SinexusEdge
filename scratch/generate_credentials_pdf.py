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
            self.drawString(40, 815, "SINEXUS EDGE — THIRD-PARTY MANAGEMENT & CREDENTIALS GUIDE")
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
        self.drawString(40, 32, "Confidential — Operations & Credentials Handover Template")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 32, page_str)

        self.restoreState()

def build_pdf(filename="Sinexus_Edge_Third_Party_Management_and_Credentials_Guide.pdf"):
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
    c_accent = colors.HexColor("#E65100")      # Amber Accent
    c_dark = colors.HexColor("#212121")        # Dark Neutral
    c_light_bg = colors.HexColor("#F4F6F8")    # Light Neutral Background
    c_border = colors.HexColor("#CFD8DC")      # Border Gray
    c_white = colors.HexColor("#FFFFFF")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
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
        Paragraph("<b>SINEXUS EDGE MONITORING SYSTEM</b><br/><font size=12 color='#FFE0B2'>Third-Party Services Management & Credentials Handover</font>", title_style),
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
        [Paragraph("<b>System Name:</b> Sinexus Edge Monitoring Platform", body_style), Paragraph("<b>Document Type:</b> Third-Party Management & Credentials", body_style)],
        [Paragraph("<b>Target Audience:</b> Sinexus IT & Operations Leads", body_style), Paragraph("<b>Classification:</b> RESTRICTED / CONFIDENTIAL", body_style)],
        [Paragraph("<b>Primary Cloud VPS:</b> AWS Lightsail (Ubuntu)", body_style), Paragraph("<b>Document Version:</b> 1.0.0 (Production)", body_style)]
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

    # Security Notice Box
    sec_notice_data = [
        [Paragraph("<b>CONFIDENTIAL SECURITY NOTICE</b>", ParagraphStyle('WarnHead', parent=table_header_style, textColor=c_white))],
        [Paragraph("This document contains sensitive configuration templates, portal management URLs, and integration parameters for production services. Store securely and restrict access to authorized system administrators only.", ParagraphStyle('WarnText', parent=body_style, textColor=colors.HexColor("#BF360C")))]
    ]
    sec_notice_table = Table(sec_notice_data, colWidths=[515])
    sec_notice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#FFF3E0")),
        ('BOX', (0, 0), (-1, -1), 0.5, c_accent),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sec_notice_table)
    story.append(Spacer(1, 14))

    # 1. Third-Party Console Directory
    story.append(Paragraph("1. Third-Party Service Consoles Directory", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    dir_data = [
        [Paragraph("Service Provider", table_header_style), Paragraph("Management Console URL", table_header_style), Paragraph("Authentication Method", table_header_style), Paragraph("Key Role in Platform", table_header_style)],
        [Paragraph("<b>AWS Lightsail</b>", table_cell_style), Paragraph("<code>https://lightsail.aws.amazon.com/</code>", table_cell_style), Paragraph("AWS IAM / SSH Key (`.pem`)", table_cell_style), Paragraph("VPS Hosting for Node.js REST API backend.", table_cell_style)],
        [Paragraph("<b>MongoDB Atlas</b>", table_cell_style), Paragraph("<code>https://cloud.mongodb.com/</code>", table_cell_style), Paragraph("MongoDB Database User Auth", table_cell_style), Paragraph("NoSQL cloud database cluster storing all collections.", table_cell_style)],
        [Paragraph("<b>Firebase Console</b>", table_cell_style), Paragraph("<code>https://console.firebase.google.com/</code>", table_cell_style), Paragraph("Service Account JSON Key", table_cell_style), Paragraph("FCM Push Notifications for mobile apps.", table_cell_style)],
        [Paragraph("<b>Google Maps API</b>", table_cell_style), Paragraph("<code>https://console.cloud.google.com/</code>", table_cell_style), Paragraph("Server API Key (IP Restricted)", table_cell_style), Paragraph("Address geocoding to GPS coordinates.", table_cell_style)],
        [Paragraph("<b>SMTP Mail Gateway</b>", table_cell_style), Paragraph("SMTP Service Provider Portal", table_cell_style), Paragraph("SMTP User & App Password", table_cell_style), Paragraph("Email OTP dispatch for auth verification.", table_cell_style)],
    ]
    dir_table = Table(dir_data, colWidths=[115, 145, 125, 130])
    dir_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(dir_table)
    story.append(Spacer(1, 14))

    # 2. Detailed Service Accounts & Handover Templates
    story.append(Paragraph("2. Service Accounts & Integration Details Template", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    # Account 1
    story.append(Paragraph("2.1 AWS Lightsail Cloud VPS", h2_style))
    a1_details = [
        "<b>Console URL:</b> <code>https://lightsail.aws.amazon.com/</code>",
        "<b>Instance Name:</b> Ubuntu 22.04 LTS (Instance: <code>monitoring_system_vps</code>)",
        "<b>Static Public IP:</b> Assigned Static IPv4",
        "<b>SSH Access Command:</b> <code>ssh -i /path/to/key.pem ubuntu@[STATIC_IP]</code>",
        "<b>Application Root:</b> <code>/home/ubuntu/monitoring_system</code>"
    ]
    for d in a1_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    # Account 2
    story.append(Paragraph("2.2 MongoDB Atlas Database Cluster", h2_style))
    a2_details = [
        "<b>Console URL:</b> <code>https://cloud.mongodb.com/</code>",
        "<b>Connection URI Template:</b> <code>mongodb+srv://[DB_USER]:[DB_PASSWORD]@[CLUSTER_URL]/monitoring_system?retryWrites=true&w=majority</code>",
        "<b>Database Name:</b> <code>monitoring_system</code>",
        "<b>Network Security:</b> Access restricted to AWS Lightsail Static IP address in Network Access Whitelist."
    ]
    for d in a2_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    # Page Break for clean layout
    story.append(PageBreak())

    # Account 3, 4, 5
    story.append(Paragraph("2.3 Firebase Cloud Messaging (FCM)", h2_style))
    a3_details = [
        "<b>Console URL:</b> <code>https://console.firebase.google.com/</code>",
        "<b>Project ID:</b> <code>sinexus-edge-monitoring</code>",
        "<b>Service Account Key File:</b> <code>./config/firebase-service-account.json</code>",
        "<b>Configuration Variable:</b> <code>FIREBASE_SERVICE_ACCOUNT=./config/firebase-service-account.json</code>"
    ]
    for d in a3_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2.4 Google Maps Platform (Geocoding API)", h2_style))
    a4_details = [
        "<b>Console URL:</b> <code>https://console.cloud.google.com/google/maps-apis/</code>",
        "<b>API Key Variable:</b> <code>GOOGLE_MAPS_API_KEY=[YOUR_API_KEY]</code>",
        "<b>Key Restriction:</b> HTTP Referrer / Server IP restricted to backend server IP."
    ]
    for d in a4_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2.5 SMTP Email Gateway (Nodemailer)", h2_style))
    a5_details = [
        "<b>SMTP Host:</b> <code>EMAIL_HOST=smtp.gmail.com</code> (Port: <code>587</code> / TLS)",
        "<b>SMTP User:</b> <code>EMAIL_USER=[ALERTS_EMAIL]</code>",
        "<b>SMTP Password:</b> <code>EMAIL_PASS=[APP_PASSWORD]</code>"
    ]
    for d in a5_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 14))

    # 3. Credential Rotation Playbook
    story.append(Paragraph("3. Credential Rotation Standard Operating Procedure (SOP)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    rot_data = [
        [Paragraph("Credential Type", table_header_style), Paragraph("Rotation Frequency", table_header_style), Paragraph("Standard Rotation Procedure", table_header_style)],
        [Paragraph("<b>JWT Secret Keys</b>", table_cell_style), Paragraph("Every 6 Months", table_cell_style), Paragraph("Update <code>JWT_SECRET</code> in <code>.env</code> and restart PM2. Users will re-login seamlessly via Refresh Tokens.", table_cell_style)],
        [Paragraph("<b>MongoDB Passwords</b>", table_cell_style), Paragraph("Every 6 Months", table_cell_style), Paragraph("Create new DB user in Atlas, update <code>MONGO_URI</code> in <code>.env</code>, test connection, remove old DB user.", table_cell_style)],
        [Paragraph("<b>Google Maps API Key</b>", table_cell_style), Paragraph("Annually / Incident", table_cell_style), Paragraph("Generate new key in GCP Console, apply IP restriction, update <code>GOOGLE_MAPS_API_KEY</code>, delete old key.", table_cell_style)],
        [Paragraph("<b>Firebase Service Account</b>", table_cell_style), Paragraph("Annually / Incident", table_cell_style), Paragraph("Generate new JSON key in Firebase Console, replace <code>firebase-service-account.json</code>, restart PM2.", table_cell_style)],
    ]
    rot_table = Table(rot_data, colWidths=[125, 115, 275])
    rot_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(rot_table)
    story.append(Spacer(1, 20))

    # Sign-off box
    app_data = [
        [Paragraph("<b>CREDENTIALS HANDOVER SIGN-OFF</b>", table_header_style), Paragraph("", table_header_style)],
        [Paragraph("<b>Handover Lead:</b> Lead DevOps Engineer", table_cell_style), Paragraph("<b>Received By:</b> Sinexus IT Security Manager", table_cell_style)],
        [Paragraph("<b>Date:</b> September 04, 2026", table_cell_style), Paragraph("<b>Status:</b> Securely Delivered & Verified", table_cell_style)]
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
    print(f"Credentials PDF successfully generated: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_pdf = "Sinexus_Edge_Third_Party_Management_and_Credentials_Guide.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
