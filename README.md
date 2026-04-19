# CampusFlow

CampusFlow is an integrated Enterprise Resource Planning (ERP) solution designed to streamline academic management and enhance campus life. It combines essential administrative tools with innovative features like anonymous communication and spatial navigation to create a modern digital campus ecosystem.

## Project Structure

```text
CampusFlow/
├── 📄 README.md               
├── 📄 app.py
├── 📄 requirements.txt
├── 📁 database/
│   ├── 📄 schema_new_features.sql
│   └── 📄 schema_attendance.sql
├── 📁 templates/              
└── 📁 static/uploads/
```


## Core Features

### Advanced Modules
- **Anonymous Chat**: A secure platform for students to communicate or report issues without revealing their identity.
- **Faculty Map**: An interactive tool to locate faculty offices and departments across the campus.
- **Lost and Found**: A centralized digital board for reporting and claiming lost items.

### Standard ERP Modules
- **Attendance Management**: Digital tracking of student and faculty presence.
- **Fees Management**: Portal for tracking fee structures, payments, and receipts.
- **Circulars and Notifications**: Real-time updates on campus news and official announcements.
- **Exam Scheduling**: Management of examination dates, venues, and seat allocations.
- **Results**: Automated grading and distribution of academic performance reports.

## Project Structure

- **app.py**: The main application entry point.
- **database/**: Contains SQL schema files for attendance and new feature implementations.
- **templates/**: Contains the HTML front-end files for the user interface.
- **static/uploads/**: Storage for user-uploaded content and media.

## Prerequisites

To run this project locally, ensure you have Python installed along with the necessary dependencies.

```bash
pip install -r requirements.txt
