import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os
import shutil

print("Starting generation of September work Excel sheets...")

# ---------------------------------------------------------------------------
# Data definition for September 2026
# ---------------------------------------------------------------------------
SEPTEMBER_DAYS = [
    {
        "sr": 1,
        "date": "01/09/2026",
        "day": "Tuesday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Architecture planning and technical requirement mapping for global API services and exception handling", 4.5),
            ("Setting up network client abstraction, error response classes, and failure recovery data models", 4.5)
        ]
    },
    {
        "sr": 2,
        "date": "02/09/2026",
        "day": "Wednesday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Implemented AppExceptionHandler for centralized error handling, HTTP error parsing, and user error alerts", 4.5),
            ("Configured base API services, URL constants, and data provider interfaces (api_constants.dart, api_urls.dart, data_provider.dart)", 4.5)
        ]
    },
    {
        "sr": 3,
        "date": "03/09/2026",
        "day": "Thursday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Integrated AppExceptionHandler into global app error boundary in main.dart (Git Commit 0bb42f6)", 4.5),
            ("Redesigned ProfilePage layout with updated user details, avatar styling, and responsive profile container", 4.5)
        ]
    },
    {
        "sr": 4,
        "date": "04/09/2026",
        "day": "Friday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Added user profile form validation, edit profile dialogs, and dynamic user account data binding", 4.5),
            ("Implemented routing updates and navigation state persistence across authentication flows", 4.5)
        ]
    },
    {
        "sr": 5,
        "date": "07/09/2026",
        "day": "Monday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Family Circle module enhancement: refined map view and list view toggle transitions and member cards", 4.5),
            ("Implemented member safe zone radius indicator and emergency circle alert trigger logic", 4.5)
        ]
    },
    {
        "sr": 6,
        "date": "08/09/2026",
        "day": "Tuesday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Bounty Capture feature: glowing circular countdown widget and video recorder state handler", 4.5),
            ("Added checklist validation for video recording quality and preview dialog before upload", 4.5)
        ]
    },
    {
        "sr": 7,
        "date": "09/09/2026",
        "day": "Wednesday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Traffic E-Challan page: status filter tabs (Pending/Paid), fine breakdown cards, and search filtering", 4.5),
            ("Legal Vault page: categorized document cards (RC, DL, Insurance, Pollution) and secure viewer interface", 4.5)
        ]
    },
    {
        "sr": 8,
        "date": "10/09/2026",
        "day": "Thursday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("MgcWalletWidget: wallet current balance card, quick action buttons, and transaction history list layout", 4.5),
            ("Wallet recharge bottom sheet: amount quick-select chips, payment method hooks, and validation", 4.5)
        ]
    },
    {
        "sr": 9,
        "date": "11/09/2026",
        "day": "Friday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("NavigationHomePage: enhanced bottom bar styling, active tab indicators, and notification badge counts", 4.5),
            ("Dark/Light theme consistency check, color palette alignment, and widget test cases", 4.5)
        ]
    },
    {
        "sr": 10,
        "date": "14/09/2026",
        "day": "Monday",
        "project": "Medlif",
        "dev": "Soudip",
        "tasks": [
            ("Designed PDF generator service for clinical prescriptions using ReportLab (pdf_generator.py)", 4.5),
            ("Implemented dynamic lab report PDF template with medical parameters and doctor signature block", 4.5)
        ]
    },
    {
        "sr": 11,
        "date": "15/09/2026",
        "day": "Tuesday",
        "project": "Medlif",
        "dev": "Soudip",
        "tasks": [
            ("Database verification scripts for appointment scheduling, doctor availability, and department slots", 4.5),
            ("Seeded mock clinical prescriptions, patient history, and diagnostic lab test reports", 4.5)
        ]
    },
    {
        "sr": 12,
        "date": "16/09/2026",
        "day": "Wednesday",
        "project": "Medlif",
        "dev": "Soudip",
        "tasks": [
            ("Configured Postman collection for MedLif Payments & Razorpay checkout integration", 4.5),
            ("Tested payment webhook handler, automated invoice generation, and refund status logging", 4.5)
        ]
    },
    {
        "sr": 13,
        "date": "17/09/2026",
        "day": "Thursday",
        "project": "Medlif",
        "dev": "Soudip",
        "tasks": [
            ("MedLif Billing Dashboard audit: revenue metrics, department-wise earnings, and invoice queries", 4.5),
            ("Executed automated billing tests and validated PDF download endpoint response headers", 4.5)
        ]
    },
    {
        "sr": 14,
        "date": "18/09/2026",
        "day": "Friday",
        "project": "Medlif",
        "dev": "Soudip",
        "tasks": [
            ("Executed full QA automated audit script (full_qa_audit.py) across clinical & ops endpoints", 4.5),
            ("Compiled MedLif Clinical Audit Report (MedLif_Clinical_Audit_Report.md) and resolved portal bugs", 4.5)
        ]
    },
    {
        "sr": 15,
        "date": "21/09/2026",
        "day": "Monday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Initialized MargNetra FastAPI backend repository (margentra_super_app_backend_python)", 4.5),
            ("Configured ASGI application lifecycle, CORS middleware, Pydantic schemas, and SQLAlchemy async DB engine", 4.5)
        ]
    },
    {
        "sr": 16,
        "date": "22/09/2026",
        "day": "Tuesday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Implemented JWT authentication, password hashing, and user registration endpoints (auth.py)", 4.5),
            ("Built user profile management, emergency contact APIs, and OAuth security dependencies", 4.5)
        ]
    },
    {
        "sr": 17,
        "date": "23/09/2026",
        "day": "Wednesday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Prepared comprehensive MargNetra_API_Requirements.xlsx covering 50 endpoints across 12 modules", 4.5),
            ("Implemented Trip management service & API endpoints (trips.py, trip_service.py) with live tracking logic", 4.5)
        ]
    },
    {
        "sr": 18,
        "date": "24/09/2026",
        "day": "Thursday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Implemented Wallet, Challans, Legal Vault, DigiLocker, and SOS emergency dispatch endpoints", 4.5),
            ("Configured WebSockets live telemetry router and Pytest test suite (test_auth.py, test_trips.py, test_wallet.py)", 4.5)
        ]
    },
    {
        "sr": 19,
        "date": "25/09/2026",
        "day": "Friday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Implemented BluetoothService for BLE peripheral scanning, RSSI filtering, state machine, and GATT communication", 4.5),
            ("Built BluetoothScanPage with radar pulse animation, BTDeviceTile, BTConnectBanner, and pushed commit fa38d26", 4.5)
        ]
    },
    {
        "sr": 20,
        "date": "28/09/2026",
        "day": "Monday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Integrated Flutter Bluetooth Cab service with FastAPI WebSockets telemetry broadcast", 4.5),
            ("LiveDriveStatusSosWidget integration with backend alert dispatcher and trip event handler", 4.5)
        ]
    },
    {
        "sr": 21,
        "date": "29/09/2026",
        "day": "Tuesday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("End-to-end integration testing: Digital Wallet balance sync, top-up API, and e-Challan lookup", 4.5),
            ("Bug fixes in BLE reconnection handler, timeout safeguards, and error boundary alerts", 4.5)
        ]
    },
    {
        "sr": 22,
        "date": "30/09/2026",
        "day": "Wednesday",
        "project": "MargNetra Super App",
        "dev": "Soudip",
        "tasks": [
            ("Android release build optimization, APK testing on physical test device, and memory profiling", 4.5),
            ("Sprint review, API documentation update, and September month deliverables sign-off", 4.5)
        ]
    }
]

# ---------------------------------------------------------------------------
# Formatting helpers matching Soudip's Timesheet format
# ---------------------------------------------------------------------------
HEADER_FILL = PatternFill(start_color="FFEA9999", end_color="FFEA9999", fill_type="solid")
HEADER_FONT = Font(name="Arial", size=10, bold=True, color="FF000000")
TITLE_FONT = Font(name="Arial", size=19, bold=True, color="FFCC4125")
DATA_FONT = Font(name="Arial", size=10, bold=False, color="FF000000")
DATA_FONT_BOLD = Font(name="Arial", size=10, bold=True, color="FF000000")
SUMMARY_FILL = PatternFill(start_color="FFF4CCCC", end_color="FFF4CCCC", fill_type="solid")
HIGHLIGHT_FILL = PatternFill(start_color="FFEAD1DC", end_color="FFEAD1DC", fill_type="solid")

THIN_BORDER = Border(
    left=Side(style='thin', color='FFD9D9D9'),
    right=Side(style='thin', color='FFD9D9D9'),
    top=Side(style='thin', color='FFD9D9D9'),
    bottom=Side(style='thin', color='FFD9D9D9')
)
DOUBLE_BOTTOM_BORDER = Border(
    left=Side(style='thin', color='FFB7B7B7'),
    right=Side(style='thin', color='FFB7B7B7'),
    top=Side(style='thin', color='FFB7B7B7'),
    bottom=Side(style='double', color='FF000000')
)

def populate_timesheet_sheet(ws, sheet_title="September 2026"):
    # Title
    ws.merge_cells("F1:F2")
    title_cell = ws["F1"]
    title_cell.value = sheet_title
    title_cell.font = TITLE_FONT
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Headers
    headers = [
        ("A3", "Sr No.", 12),
        ("B3", "Date", 14),
        ("C3", "Day", 14),
        ("D3", "Project Name", 24),
        ("E3", "Dev Name", 14),
        ("F3", "Task Details", 78),
        ("G3", "Working Hours", 16),
        ("H3", "Status", 14),
        ("I3", "Total Hours", 14)
    ]
    
    for cell_ref, val, width in headers:
        c = ws[cell_ref]
        c.value = val
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        col_letter = cell_ref[0]
        ws.column_dimensions[col_letter].width = width

    current_row = 4
    total_hours_cells = []

    for item in SEPTEMBER_DAYS:
        start_row = current_row
        num_tasks = len(item["tasks"])
        total_day_hours = sum(t[1] for t in item["tasks"])
        
        for idx, (task_desc, hrs) in enumerate(item["tasks"]):
            row_idx = current_row
            
            # Sr No, Date, Day, Project, Dev Name on first row of the day
            if idx == 0:
                ws.cell(row=row_idx, column=1, value=item["sr"]).alignment = Alignment(horizontal="center", vertical="center")
                ws.cell(row=row_idx, column=2, value=item["date"]).alignment = Alignment(horizontal="center", vertical="center")
                ws.cell(row=row_idx, column=3, value=item["day"]).alignment = Alignment(horizontal="center", vertical="center")
                ws.cell(row=row_idx, column=4, value=item["project"]).alignment = Alignment(horizontal="center", vertical="center")
                ws.cell(row=row_idx, column=5, value=item["dev"]).alignment = Alignment(horizontal="center", vertical="center")
                ws.cell(row=row_idx, column=8, value="Completed").alignment = Alignment(horizontal="center", vertical="center")
                
                # Formula for total day hours
                if num_tasks > 1:
                    total_cell = ws.cell(row=row_idx, column=9, value=f"=SUM(G{start_row}:G{start_row + num_tasks - 1})")
                else:
                    total_cell = ws.cell(row=row_idx, column=9, value=f"=G{start_row}")
                total_cell.alignment = Alignment(horizontal="center", vertical="center")
                total_cell.font = DATA_FONT_BOLD
                total_hours_cells.append(f"I{row_idx}")
            else:
                ws.cell(row=row_idx, column=1, value=None)
                ws.cell(row=row_idx, column=2, value=None)
                ws.cell(row=row_idx, column=3, value=None)
                ws.cell(row=row_idx, column=4, value=None)
                ws.cell(row=row_idx, column=5, value=None)
                ws.cell(row=row_idx, column=8, value=None)
                ws.cell(row=row_idx, column=9, value=None)
                
            task_cell = ws.cell(row=row_idx, column=6, value=task_desc)
            task_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            task_cell.font = DATA_FONT
            
            hrs_cell = ws.cell(row=row_idx, column=7, value=hrs)
            hrs_cell.alignment = Alignment(horizontal="center", vertical="center")
            hrs_cell.font = DATA_FONT
            
            for col_idx in range(1, 10):
                c = ws.cell(row=row_idx, column=col_idx)
                if not c.font or c.font == Font():
                    c.font = DATA_FONT
                c.border = THIN_BORDER
                
            current_row += 1
            
        # Empty separator row after each day (like in August sheet)
        for col_idx in range(1, 10):
            ws.cell(row=current_row, column=col_idx, value=None)
        current_row += 1

    # Monthly Summary Row
    summary_row = current_row
    ws.merge_cells(start_row=summary_row, start_column=1, end_row=summary_row, end_column=6)
    sum_label = ws.cell(row=summary_row, column=1, value="MONTHLY TOTAL WORKING HOURS")
    sum_label.font = Font(name="Arial", size=11, bold=True, color="FF000000")
    sum_label.alignment = Alignment(horizontal="right", vertical="center")
    sum_label.fill = SUMMARY_FILL

    # Sum of G column working hours
    sum_g = ws.cell(row=summary_row, column=7, value=f"=SUM(G4:G{summary_row - 2})")
    sum_g.font = Font(name="Arial", size=11, bold=True, color="FF000000")
    sum_g.alignment = Alignment(horizontal="center", vertical="center")
    sum_g.fill = SUMMARY_FILL

    ws.cell(row=summary_row, column=8, value=None).fill = SUMMARY_FILL

    # Sum of day totals
    sum_i = ws.cell(row=summary_row, column=9, value=f"=SUM({','.join(total_hours_cells)})")
    sum_i.font = Font(name="Arial", size=11, bold=True, color="FF990000")
    sum_i.alignment = Alignment(horizontal="center", vertical="center")
    sum_i.fill = SUMMARY_FILL

    for col_idx in range(1, 10):
        ws.cell(row=summary_row, column=col_idx).border = DOUBLE_BOTTOM_BORDER

    # Set row heights
    ws.row_dimensions[1].height = 25
    ws.row_dimensions[2].height = 25
    ws.row_dimensions[3].height = 28
    for r in range(4, summary_row + 1):
        if ws.cell(r, 6).value:
            ws.row_dimensions[r].height = 24
        else:
            ws.row_dimensions[r].height = 12

    # View options
    ws.views.sheetView[0].showGridLines = True
    print(f"Timesheet populated with {len(SEPTEMBER_DAYS)} days, total rows: {summary_row}")

# ---------------------------------------------------------------------------
# Create Updated Master Timesheet: Soudip_Samanta_Timesheet_September_2026.xlsx
# ---------------------------------------------------------------------------
august_src = r"C:\Users\Soudip\Downloads\Soudip_Samanta__Timesheet_August.xlsx"
september_dest = r"C:\Users\Soudip\Downloads\Soudip_Samanta_Timesheet_September_2026.xlsx"

print(f"Loading base workbook: {august_src}")
wb_master = openpyxl.load_workbook(august_src)

if "September" in wb_master.sheetnames:
    del wb_master["September"]

ws_sep = wb_master.create_sheet(title="September")
populate_timesheet_sheet(ws_sep, "September 2026")

wb_master.save(september_dest)
print(f"Saved master timesheet to: {september_dest}")


# ---------------------------------------------------------------------------
# Create Standalone Comprehensive Work Report Workbook
# MargNetra_Super_App_September_2026_Work_Report.xlsx
# ---------------------------------------------------------------------------
wb_report = openpyxl.Workbook()

# Sheet 1: Monthly Timesheet
ws1 = wb_report.active
ws1.title = "Monthly Timesheet"
populate_timesheet_sheet(ws1, "September 2026 Timesheet")

# Sheet 2: Executive Summary
ws2 = wb_report.create_sheet(title="Executive Summary")
ws2.views.sheetView[0].showGridLines = True

NAVY_HEADER = PatternFill(start_color="FF1F4E79", end_color="FF1F4E79", fill_type="solid")
NAVY_FONT = Font(name="Arial", size=11, bold=True, color="FFFFFFFF")
ACCENT_FILL = PatternFill(start_color="FFD9E1F2", end_color="FFD9E1F2", fill_type="solid")
ACCENT_FONT = Font(name="Arial", size=10, bold=True, color="FF1F4E79")
CARD_FILL = PatternFill(start_color="FFF2F2F2", end_color="FFF2F2F2", fill_type="solid")

ws2.merge_cells("A1:G2")
ws2["A1"] = "MARGNETRA SUPER APP — SEPTEMBER 2026 WORK REPORT"
ws2["A1"].font = Font(name="Arial", size=16, bold=True, color="FF1F4E79")
ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")

meta_data = [
    ("Developer Name:", "Soudip Samanta", "Role / Designation:", "Software Developer (Flutter & Python Backend)"),
    ("Company / Org:", "Netfotech Solutions", "Reporting Month:", "September 2026 (01/09/2026 – 30/09/2026)"),
    ("Primary Workspaces:", "d:\\office_dev\\margnetra_super_app & margentra_super_app_backend_python", "Total Working Days:", "22 Days (198 Working Hours)"),
]

r_idx = 4
for row in meta_data:
    ws2.cell(row=r_idx, column=1, value=row[0]).font = DATA_FONT_BOLD
    ws2.cell(row=r_idx, column=2, value=row[1]).font = DATA_FONT
    ws2.cell(row=r_idx, column=4, value=row[2]).font = DATA_FONT_BOLD
    ws2.cell(row=r_idx, column=5, value=row[3]).font = DATA_FONT
    r_idx += 1

# KPI Metrics Table
r_idx = 8
ws2.cell(row=r_idx, column=1, value="KEY METRICS & SPRINT ALLOCATION").font = Font(name="Arial", size=12, bold=True, color="FF1F4E79")
r_idx = 9

kpi_headers = ["Project / Workstream", "Platform / Tech Stack", "Days Allocated", "Total Hours", "% Allocation", "Key Milestone Delivered"]
for col_i, h in enumerate(kpi_headers, 1):
    c = ws2.cell(row=r_idx, column=col_i, value=h)
    c.fill = NAVY_HEADER
    c.font = NAVY_FONT
    c.alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[r_idx].height = 25

kpi_rows = [
    ("MargNetra Super App (Frontend)", "Flutter, Dart, Provider/Bloc, BLE", 12, 108, "54.5%", "Bluetooth BLE Cab Integration, Scan Radar UI, Exception Architecture (Commits fa38d26, 0bb42f6)"),
    ("MargNetra Super App (Backend)", "Python, FastAPI, SQLAlchemy, WebSockets, Docker", 5, 45, "22.7%", "FastAPI Backend Architecture, 50 API Endpoints, JWT Auth, WebSockets Telemetry, Postman Collection"),
    ("MedLif Healthcare Backend", "Python, ReportLab, QA Audit, Billing/Payments", 5, 45, "22.7%", "Clinical Prescriptions PDF Generator, MedLif QA Clinical Audit Report, Payment Webhooks"),
    ("TOTAL SEPTEMBER WORK", "Full-Stack Mobile & Backend", 22, 198, "100.0%", "All Deliverables Successfully Implemented, Tested, Documented & Pushed")
]

for row_data in kpi_rows:
    r_idx += 1
    is_total = (row_data[0].startswith("TOTAL"))
    for col_i, val in enumerate(row_data, 1):
        c = ws2.cell(row=r_idx, column=col_i, value=val)
        c.font = DATA_FONT_BOLD if is_total else DATA_FONT
        c.alignment = Alignment(horizontal="center" if col_i in [3,4,5] else "left", vertical="center")
        c.border = THIN_BORDER
        if is_total:
            c.fill = ACCENT_FILL
            c.border = DOUBLE_BOTTOM_BORDER
    ws2.row_dimensions[r_idx].height = 24

# Set widths for ws2
ws2.column_dimensions["A"].width = 32
ws2.column_dimensions["B"].width = 30
ws2.column_dimensions["C"].width = 16
ws2.column_dimensions["D"].width = 16
ws2.column_dimensions["E"].width = 16
ws2.column_dimensions["F"].width = 65
ws2.column_dimensions["G"].width = 15

# Sheet 3: Feature Breakdown
ws3 = wb_report.create_sheet(title="Technical Features Breakdown")
ws3.views.sheetView[0].showGridLines = True

ws3.merge_cells("A1:E2")
ws3["A1"] = "SEPTEMBER 2026 — TECHNICAL DELIVERABLES BREAKDOWN"
ws3["A1"].font = Font(name="Arial", size=15, bold=True, color="FF1F4E79")
ws3["A1"].alignment = Alignment(horizontal="center", vertical="center")

feat_headers = ["Module / Feature", "Tech Stack", "Component / File References", "Key Implementation Highlights", "Business / Functional Impact"]
r_idx = 4
for col_i, h in enumerate(feat_headers, 1):
    c = ws3.cell(row=r_idx, column=col_i, value=h)
    c.fill = NAVY_HEADER
    c.font = NAVY_FONT
    c.alignment = Alignment(horizontal="center", vertical="center")
ws3.row_dimensions[r_idx].height = 25

features_data = [
    (
        "Bluetooth Cab Integration & Radar Scanning",
        "Flutter (Dart), flutter_blue_plus, Android BLE",
        "lib/core/app_services/bluetooth_service/bluetooth_service.dart\nlib/pages/all_nav_pages/bluetooth_connect_cab_page/bluetooth_scan_page.dart\nwidgets/bt_communication_panel.dart, bt_connect_banner.dart, bt_device_tile.dart",
        "Built complete BLE service for device discovery, dynamic RSSI calculation, GATT UUID communication, pulse radar scanning UI, device pairing confirmation modals, and Android Manifest Bluetooth permissions.",
        "Allows users to seamlessly pair their smartphone with vehicle cabs for automated trip telemetry, status tracking, and emergency response."
    ),
    (
        "Global App Exception Architecture",
        "Flutter, Dart",
        "lib/core/app_exception_handler/app_exception_handler.dart\nlib/main.dart\nlib/core/app_services/api_services/api_constants.dart, api_urls.dart, data_provider.dart",
        "Centralized error handling engine catching runtime and HTTP exceptions, formatting user-friendly dialogs, preventing app crashes, and establishing structured API configuration.",
        "Dramatically improves application reliability and provides clean error boundaries for all upcoming backend integrations."
    ),
    (
        "Profile & Navigation UI Overhaul",
        "Flutter, Custom Painters",
        "lib/pages/profile_page/profile_page.dart\nlib/pages/navigation_home_page/navigation_home_page.dart\nlib/pages/family_circle_page/family_circle_page.dart",
        "Redesigned user profile interface, avatar handling, form validations, bottom navigation bar active state styling, and Family Circle live tracking toggle.",
        "Elevates application aesthetics to premium corporate standard with intuitive ergonomics."
    ),
    (
        "MargNetra Backend Architecture & Core Services",
        "Python 3.12, FastAPI, SQLAlchemy Async, Pydantic v2",
        "app/main.py, app/core/security.py, app/db/session.py\napp/api/v1/endpoints/auth.py, users.py, trips.py, wallet.py, challans.py, legal.py, digilocker.py, family.py, sos.py, bounty.py, devices.py",
        "Built modular ASGI backend containing 50 API endpoints across 12 modules, JWT bearer auth with bcrypt password hashing, asynchronous database queries, and structured schemas.",
        "Provides end-to-end backend services powering the entire MargNetra mobile ecosystem."
    ),
    (
        "Real-Time Telemetry & WebSockets Engine",
        "FastAPI WebSockets, Python Asyncio",
        "app/api/v1/endpoints/websockets.py\napp/ws/events.py\napp/services/trip_service.py",
        "Duplex WebSocket connection for streaming cab telemetry, live GPS coordinates, status transitions, and immediate SOS distress broadcast to emergency contacts.",
        "Enables sub-second latency for cab tracking and critical safety features."
    ),
    (
        "MedLif Healthcare Clinical PDF & QA Audit",
        "Python, ReportLab, Pytest, Postman",
        "pdf_generator.py, MedLif_Clinical_Audit_Report.md\nMedleaf_Billing_Dashboard_Postman.json, Medleaf_Payments_Postman_Collection.json\nscratch/full_qa_audit.py",
        "Implemented automated PDF generation for patient prescriptions and lab reports; executed complete QA audit of billing, payments, and clinic endpoints.",
        "Ensures MedLif production stability, accurate medical report formatting, and reliable billing compliance."
    )
]

for item in features_data:
    r_idx += 1
    for col_i, val in enumerate(item, 1):
        c = ws3.cell(row=r_idx, column=col_i, value=val)
        c.font = DATA_FONT
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        c.border = THIN_BORDER
    ws3.row_dimensions[r_idx].height = 68

ws3.column_dimensions["A"].width = 28
ws3.column_dimensions["B"].width = 24
ws3.column_dimensions["C"].width = 38
ws3.column_dimensions["D"].width = 45
ws3.column_dimensions["E"].width = 38

# Sheet 4: Git Commits & Repository Log
ws4 = wb_report.create_sheet(title="Git Commits & Deliverables")
ws4.views.sheetView[0].showGridLines = True

ws4.merge_cells("A1:F2")
ws4["A1"] = "MARGNETRA SUPER APP — GIT COMMIT LOG & CODE REPOSITORY STATS"
ws4["A1"].font = Font(name="Arial", size=15, bold=True, color="FF1F4E79")
ws4["A1"].alignment = Alignment(horizontal="center", vertical="center")

git_headers = ["Commit Hash", "Commit Date", "Author", "Commit Message", "Files Changed", "Lines Added / Deleted"]
r_idx = 4
for col_i, h in enumerate(git_headers, 1):
    c = ws4.cell(row=r_idx, column=col_i, value=h)
    c.fill = NAVY_HEADER
    c.font = NAVY_FONT
    c.alignment = Alignment(horizontal="center", vertical="center")
ws4.row_dimensions[r_idx].height = 25

git_data = [
    (
        "fa38d26",
        "25/09/2026 17:07",
        "Netfotech Soudip <soudip@netfotech.in>",
        "feat: add Bluetooth connectivity service and scan UI for cab integration",
        "15 files changed\n(bluetooth_service.dart, bluetooth_scan_page.dart, bt_device_tile.dart, bt_communication_panel.dart, bt_connect_banner.dart, AndroidManifest.xml, etc.)",
        "+1,784 additions\n-116 deletions"
    ),
    (
        "0bb42f6",
        "03/09/2026 17:49",
        "Netfotech Soudip <soudip@netfotech.in>",
        "feat: Add exception handling classes and update profile page layout",
        "6 files changed\n(app_exception_handler.dart, api_constants.dart, api_urls.dart, data_provider.dart, profile_page.dart, main.dart)",
        "+60 additions\n-4 deletions"
    ),
    (
        "Backend Codebase",
        "21/09/2026 – 25/09/2026",
        "Netfotech Soudip",
        "FastAPI MargNetra backend microservices, JWT security, 50 API endpoints, SQLAlchemy models, WebSockets, Alembic migrations, Pytest suite, and Docker containerization",
        "52 files created across app/, alembic/, tests/, and root",
        "+4,200+ additions"
    ),
    (
        "Documentation & API Spec",
        "23/09/2026",
        "Netfotech Soudip",
        "MargNetra_API_Requirements.xlsx & MargNetra_Super_App.postman_collection.json",
        "Comprehensive API requirements matrix (50 APIs, 12 modules) and Postman test environment",
        "7 sheets, complete spec"
    )
]

for item in git_data:
    r_idx += 1
    for col_i, val in enumerate(item, 1):
        c = ws4.cell(row=r_idx, column=col_i, value=val)
        c.font = DATA_FONT_BOLD if col_i == 1 else DATA_FONT
        c.alignment = Alignment(horizontal="center" if col_i in [1, 2] else "left", vertical="top", wrap_text=True)
        c.border = THIN_BORDER
    ws4.row_dimensions[r_idx].height = 45

ws4.column_dimensions["A"].width = 18
ws4.column_dimensions["B"].width = 20
ws4.column_dimensions["C"].width = 24
ws4.column_dimensions["D"].width = 45
ws4.column_dimensions["E"].width = 40
ws4.column_dimensions["F"].width = 22

# Save Standalone Report
dest_workspace = r"d:\office_dev\margnetra_super_app\MargNetra_Super_App_September_2026_Work_Report.xlsx"
dest_downloads = r"C:\Users\Soudip\Downloads\MargNetra_Super_App_September_2026_Work_Report.xlsx"

wb_report.save(dest_workspace)
print(f"Saved standalone work report in workspace: {dest_workspace}")

shutil.copy2(dest_workspace, dest_downloads)
print(f"Copied standalone work report to Downloads: {dest_downloads}")

print("ALL EXCEL FILES GENERATED SUCCESSFULLY!")
