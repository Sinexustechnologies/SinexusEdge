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
            self.drawString(40, 815, "SINEXUS EDGE — INTEGRATION ARCHITECTURE DOCUMENT")
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
        self.drawString(40, 32, "Confidential — Integration & Interface Specifications")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 32, page_str)

        self.restoreState()

def build_pdf(filename="Sinexus_Edge_Integration_Architecture_Document.pdf"):
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
    c_accent = colors.HexColor("#6A1B9A")      # Purple Accent
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
        Paragraph("<b>SINEXUS EDGE MONITORING SYSTEM</b><br/><font size=12 color='#E1BEE7'>Integration Architecture & Interface Document</font>", title_style),
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
        [Paragraph("<b>System Name:</b> Sinexus Edge Monitoring Platform", body_style), Paragraph("<b>Document Type:</b> Integration Architecture Specification", body_style)],
        [Paragraph("<b>Backend API:</b> Node.js, Express, Socket.IO", body_style), Paragraph("<b>External APIs:</b> Google Maps, Firebase FCM, SMTP", body_style)],
        [Paragraph("<b>Hardware Ingestion:</b> HTTP / MQTT Telemetry Nodes", body_style), Paragraph("<b>Document Version:</b> 1.0.0 (Production)", body_style)]
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

    # 1. Executive Summary & Integration Overview
    story.append(Paragraph("1. Executive Summary & Integration Overview", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    exec_p = (
        "The <b>Integration Architecture Document</b> defines the protocols, interfaces, payload contracts, security policies, and error handling "
        "mechanisms connecting the Sinexus Edge backend with external cloud ecosystems, third-party microservices, IoT hardware nodes, and client applications. "
        "The system relies on loose coupling, asynchronous event buses, and resilient API adapters to maintain high uptime and real-time responsiveness."
    )
    story.append(Paragraph(exec_p, body_style))
    story.append(Spacer(1, 10))

    # Integration Components Summary Table
    story.append(Paragraph("<b>Integration Subsystems & Interfaces:</b>", h2_style))
    sub_data = [
        [Paragraph("Integration Interface", table_header_style), Paragraph("Protocol / Format", table_header_style), Paragraph("Purpose & Operational Description", table_header_style)],
        [Paragraph("<b>IoT Telemetry Ingestion</b>", table_cell_style), Paragraph("HTTP POST / MQTT (JSON)", table_cell_style), Paragraph("Ingests real-time hardware telemetry (Odor ppm, Usage Counter, Feedback hits) from ESP32 gateway nodes installed at toilet facilities.", table_cell_style)],
        [Paragraph("<b>Firebase FCM Push Gateway</b>", table_cell_style), Paragraph("HTTPS / FCM HTTP v1 API", table_cell_style), Paragraph("Dispatches immediate push notification alerts to cleaning staff mobile devices when urgent cleaning tasks are generated.", table_cell_style)],
        [Paragraph("<b>Google Maps Location API</b>", table_cell_style), Paragraph("HTTPS REST / JSON", table_cell_style), Paragraph("Translates facility street addresses to exact geographical GPS coordinates (lat/lng) and reverse-geocodes coordinates.", table_cell_style)],
        [Paragraph("<b>Email Dispatch Gateway</b>", table_cell_style), Paragraph("SMTP / TLS (Nodemailer)", table_cell_style), Paragraph("Delivers 6-digit OTP verification codes for admin onboarding, staff verification, and self-service password resets.", table_cell_style)],
        [Paragraph("<b>WebSocket Real-time Bus</b>", table_cell_style), Paragraph("WSS / Socket.IO (JSON)", table_cell_style), Paragraph("Maintains full-duplex persistent connections with Synxeus Frontend clients for real-time alert updates and status syncing.", table_cell_style)],
        [Paragraph("<b>MongoDB Atlas Cluster</b>", table_cell_style), Paragraph("MongoDB Wire Protocol / TLS 1.3", table_cell_style), Paragraph("Encrypted persistence tier connection pool handling database queries, indexes, and transactional audit logs.", table_cell_style)],
    ]
    sub_table = Table(sub_data, colWidths=[130, 115, 270])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 14))

    # 2. Detailed Interface Specifications
    story.append(Paragraph("2. Detailed Interface Specifications", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    # Interface 1
    story.append(Paragraph("Interface 1: Hardware IoT Telemetry Ingestion", h2_style))
    if1_details = [
        "<b>Endpoint Contract:</b> <code>POST /api/telemetry</code> or MQTT topic <code>sinexus/telemetry/[device_uid]</code>",
        "<b>Authentication:</b> Device Hardware UID (<code>device_uid</code>) validation against registered <code>Device</code> collection.",
        "<b>Payload Schema:</b> <code>{ \"device_uid\": \"DEV-101\", \"OdorSensVal\": 480, \"Counter\": 142, \"feedback\": \"POOR\" }</code>",
        "<b>Processing Logic:</b> Updates <code>LatestDeviceStatus</code> document in MongoDB and triggers <code>alertClassifier.js</code> to generate anomaly alerts if thresholds are breached."
    ]
    for d in if1_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    # Interface 2
    story.append(Paragraph("Interface 2: Firebase Cloud Messaging (FCM) Push Gateway", h2_style))
    if2_details = [
        "<b>Service Adapter:</b> <code>notificationService.js</code> powered by Firebase Admin SDK.",
        "<b>Credentials Security:</b> Authenticated using service account private key stored in environment variables.",
        "<b>FCM Token Lifecycle:</b> Upon user login, client sends <code>fcmToken</code>. Backend unbinds token from other users and stores it in <code>User.fcmTokens</code> array.",
        "<b>Payload Structure:</b> <code>{ \"notification\": { \"title\": \"New Task Assigned\", \"body\": \"Urgent cleaning required at Floor 1 Restroom\" }, \"data\": { \"taskId\": \"...\", \"type\": \"TASK_ASSIGNED\" } }</code>"
    ]
    for d in if2_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    # Page Break for clean sectioning
    story.append(PageBreak())

    # Interface 3 & 4
    story.append(Paragraph("Interface 3: Google Maps Platform Geocoding Service", h2_style))
    if3_details = [
        "<b>Service Adapter:</b> <code>googleMapsService.js</code> invoking Google Maps Geocoding REST API.",
        "<b>Geocoding Flow:</b> Resolves textual address (e.g., <i>'Terminal 1, Delhi Airport'</i>) to GPS Coordinates <code>{ lat: 28.5562, lng: 77.1000 }</code>.",
        "<b>Reverse Geocoding Flow:</b> Resolves latitude and longitude coordinates back to formatted street address string.",
        "<b>API Key Management:</b> Server-side API Key restricted by IP address to prevent unauthorized quota usage."
    ]
    for d in if3_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Interface 4: Email Dispatch & OTP Gateway", h2_style))
    if4_details = [
        "<b>Service Adapter:</b> <code>emailService.js</code> utilizing Nodemailer with SMTP transport.",
        "<b>OTP Delivery:</b> Sends HTML-formatted emails containing 6-digit OTP codes for admin onboarding and staff password resets.",
        "<b>Expiration Protocol:</b> Generated OTPs expire automatically after 10 minutes (enforced by <code>Otp.expiresAt</code> index)."
    ]
    for d in if4_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Interface 5: Socket.IO Real-time WebSocket Event Bus", h2_style))
    if5_details = [
        "<b>Connection Protocol:</b> WebSocket (WSS) upgraded from HTTP.",
        "<b>Key Broadcast Events:</b>",
        "&nbsp;&nbsp;&nbsp;&nbsp;- <code>assignments_updated</code>: Emitted when device assignments are updated.",
        "&nbsp;&nbsp;&nbsp;&nbsp;- <code>alert_created</code>: Emitted when a new Moderate/Urgent alert is triggered.",
        "&nbsp;&nbsp;&nbsp;&nbsp;- <code>task_updated</code>: Emitted when staff starts, submits, or verifies a cleaning task."
    ]
    for d in if5_details:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 14))

    # 3. Security & Resilience Protocols
    story.append(Paragraph("3. Security, Authentication & Resiliency Protocols", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    sec_data = [
        [Paragraph("Security Layer", table_header_style), Paragraph("Enforced Protocol", table_header_style), Paragraph("Resiliency & Fallback Strategy", table_header_style)],
        [Paragraph("<b>Transport Security</b>", table_cell_style), Paragraph("TLS 1.3 / HTTPS / WSS", table_cell_style), Paragraph("All API calls and WebSockets encrypted in transit.", table_cell_style)],
        [Paragraph("<b>API Authentication</b>", table_cell_style), Paragraph("Bearer JWT Access Token", table_cell_style), Paragraph("15-minute token expiry. Refresh tokens handle seamless re-authentication.", table_cell_style)],
        [Paragraph("<b>API Key Isolation</b>", table_cell_style), Paragraph("Environment Variables (<code>.env</code>)", table_cell_style), Paragraph("Keys never exposed to client side. Restricted by IP on Cloud Console.", table_cell_style)],
        [Paragraph("<b>Third-party Outages</b>", table_cell_style), Paragraph("Try-Catch & Graceful Fallback", table_cell_style), Paragraph("If Google Maps API fails, device is created with location name without blocking.", table_cell_style)],
    ]
    sec_table = Table(sec_data, colWidths=[120, 150, 245])
    sec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c_white, c_light_bg]),
    ]))
    story.append(sec_table)
    story.append(Spacer(1, 20))

    # Sign-off box
    app_data = [
        [Paragraph("<b>INTEGRATION SPECIFICATION SIGN-OFF</b>", table_header_style), Paragraph("", table_header_style)],
        [Paragraph("<b>Integration Engineer:</b> Senior Integration Lead", table_cell_style), Paragraph("<b>Approved By:</b> Sinexus Lead Architect", table_cell_style)],
        [Paragraph("<b>Date:</b> September 04, 2026", table_cell_style), Paragraph("<b>Status:</b> Approved for Production Integration", table_cell_style)]
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
    print(f"Integration PDF successfully generated: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_pdf = "Sinexus_Edge_Integration_Architecture_Document.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
