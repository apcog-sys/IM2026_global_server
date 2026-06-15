# System Configuration Manager - Features Documentation

## Overview
The application now includes three main feature modules:

### 1. System Configuration (Existing)
- **Database Configuration**: Connect to MySQL database
- **Network Configuration**: Manage network settings with full CRUD operations

### 2. Security Entities (NEW)
A comprehensive system to register and manage security entities (servers, applications, and services).

#### Features:
- **Three Entity Types**: 
  - Security Servers
  - Applications
  - Services

- **Entity Information**:
  - ID (Primary Key - unique identifier)
  - Type (security_server, application, service)
  - Name (required)
  - Description (optional)
  - Version (track version numbers)
  - Status (Active, Inactive, Deprecated)
  - Contact Email (for responsible person/team)
  - Tags (comma-separated for categorization)
  
- **Full CRUD Operations**:
  - Create new entities
  - View all entities organized by type
  - Edit existing entity information
  - Delete entities
  - Auto-timestamps (created_at, updated_at)

- **UI Tabs**:
  - Security Servers tab
  - Applications tab
  - Services tab
  - Each with dedicated table and management interface

### 3. Registration & Approvals (NEW)
A complete workflow system for registering entities and managing approval requests with attached proof documents.

#### Features:
- **Approval Request Creation**:
  - Request ID (unique identifier)
  - Entity ID (reference to security entity)
  - Entity Type (security_server, application, service)
  - Status (Pending, Approved, Rejected)
  - Requested By (requester name)
  - Comments (additional notes)

- **Document Management**:
  - Multiple file upload support (PDF, DOC, DOCX, JPG, PNG, TXT)
  - Files stored as BLOB in database
  - File metadata tracked (file_name, file_type, file_size, uploaded_by, uploaded_at)
  - Download capability for stored documents
  - Delete documents as needed

- **Approval Workflow**:
  - Request submission
  - Approval tracking:
    - Approved By (name of approver)
    - Approved Date (timestamp)
  - Status filtering (Pending, Approved, Rejected)
  - Approval history with timestamps

- **Full CRUD Operations**:
  - Create approval requests
  - View all approvals with filtering
  - View detailed approval with attached documents
  - Update approval status and comments
  - Delete approval requests
  - Upload/download proof documents
  - Delete individual documents

## Database Schema

### security_entities Table
```sql
CREATE TABLE security_entities (
    id VARCHAR(100) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(255),
    contact_email VARCHAR(255),
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
```

### registration_approvals Table
```sql
CREATE TABLE registration_approvals (
    id VARCHAR(100) PRIMARY KEY,
    entity_id VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    requested_by VARCHAR(255) NOT NULL,
    requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by VARCHAR(255),
    approved_date TIMESTAMP NULL,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES security_entities(id) ON DELETE CASCADE
)
```

### approval_documents Table
```sql
CREATE TABLE approval_documents (
    id VARCHAR(100) PRIMARY KEY,
    approval_id VARCHAR(100) NOT NULL,
    file_name VARCHAR(255),
    file_type VARCHAR(100),
    file_data LONGBLOB NOT NULL,
    file_size INT,
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (approval_id) REFERENCES registration_approvals(id) ON DELETE CASCADE
)
```

## API Endpoints

### Security Entities
- `POST /api/security-entities` - Create entity
- `GET /api/security-entities` - Get all entities
- `GET /api/security-entities?entity_type=security_server` - Filter by type
- `GET /api/security-entities/{id}` - Get specific entity
- `PUT /api/security-entities/{id}` - Update entity
- `DELETE /api/security-entities/{id}` - Delete entity

### Registration Approvals
- `POST /api/registration-approvals` - Create approval request
- `GET /api/registration-approvals` - Get all approvals
- `GET /api/registration-approvals?status=pending` - Filter by status
- `GET /api/registration-approvals?entity_type=security_server` - Filter by entity type
- `GET /api/registration-approvals/{id}` - Get approval with documents
- `PUT /api/registration-approvals/{id}` - Update approval
- `DELETE /api/registration-approvals/{id}` - Delete approval

### Approval Documents
- `POST /api/registration-approvals/{id}/upload-document` - Upload proof document
- `GET /api/registration-approvals/{id}/documents` - Get all documents
- `GET /api/approval-documents/{id}/download` - Download document
- `DELETE /api/approval-documents/{id}` - Delete document

### Database
- `POST /api/init-db` - Initialize database tables (auto-called on page load)

## Usage Workflow

### Creating a Security Entity
1. Navigate to "Security Entities" in sidebar
2. Click on the entity type (Security Servers, Applications, or Services)
3. Click "Add [Entity Type]" button
4. Fill in required fields (ID, Name)
5. Optionally add description, version, status, contact email, and tags
6. Click "Save Entity"

### Creating an Approval Request
1. Navigate to "Approvals" → "Approval Requests" in sidebar
2. Click "New Approval Request" button
3. Fill in the form:
   - ID: Unique identifier for the approval
   - Entity ID: ID of the security entity to approve
   - Entity Type: Type of entity
   - Status: Set initial status (pending by default)
   - Requested By: Name of requester
   - Comments: Any additional notes
   - Upload Proof Documents: Attach supporting files
4. Click "Create Approval Request"

### Viewing Approval Details
1. In Approval Requests table, click the eye icon (👁)
2. View approval information and all attached documents
3. Download or delete documents as needed

### Updating Approval Status
1. Click the edit (pencil) icon on an approval request
2. Update the status (Pending, Approved, Rejected)
3. Update comments if needed
4. Click "Save Approval"

## Features Highlights

✓ **Full CRUD Operations** - Create, Read, Update, Delete for all entities
✓ **File Storage as BLOB** - Documents stored directly in database
✓ **Multiple File Support** - Upload multiple proof documents per approval
✓ **File Management** - Download and delete individual documents
✓ **Status Tracking** - Track approval workflow from request to approval
✓ **Filtering & Search** - Filter by status, entity type
✓ **Responsive Design** - Works on desktop and mobile
✓ **Bootstrap 5 Styling** - Modern, professional UI
✓ **Timestamps** - Automatic tracking of request and approval dates
✓ **Referential Integrity** - Foreign key constraints between tables

## Technologies Used
- **Backend**: FastAPI, MySQL Connector
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Database**: MySQL with BLOB storage for files
- **API**: RESTful endpoints for all operations

## Next Steps
1. Configure database connection in the UI
2. Initialize database tables (auto-done on first load after DB config)
3. Start creating security entities
4. Create approval requests with documents
5. Track and manage approvals
