implementationplan.md
Multi-Site Camera Streaming Platform
Website Development Implementation Plan
1. Project Objective
Develop a web-based Video Management System (VMS) that allows:
Camera registration and management
Site management
User management
Camera location assignment
Live HLS stream viewing
Site-based access control
Stream control (Play/Pause)
Camera migration tracking
Monitoring dashboard
The website acts as the central control panel for the entire streaming ecosystem.
2. Recommended Technology Stack
Frontend
React.js
Vite
Tailwind CSS
React Router
Axios
HLS.js
React Query / TanStack Query
Backend
Flask
Flask-JWT-Extended
Flask-CORS
PyMongo
Database
MongoDB Atlas
3. User Roles
Super Admin
Permissions:
Create users
Create sites
Register cameras
Assign camera locations
Assign users to sites
View all sites
Pause streams
Resume streams
User
Permissions:
Login
View assigned sites
View assigned camera streams
View camera details
Cannot:
Register cameras
Create users
Pause streams
Modify locations
4. Database Design
Users Collection
{
  
"_id"
:
 
""
,
  
"username"
:
 
""
,
  
"password_hash"
:
 
""
,
  
"role"
:
 
"admin"
,
  
"assigned_sites"
:
 
[
    
"SITE1"
,
    
"SITE2"
  
]
,
  
"created_at"
:
 
""
}
Sites Collection
{
  
"_id"
:
 
""
,
  
"site_id"
:
 
"SITE1"
,
  
"site_name"
:
 
"Factory A"
,
  
"local_server_id"
:
 
"LS001"
,
  
"status"
:
 
"active"
}
Cameras Collection
{
  
"_id"
:
 
""
,
  
"camera_code"
:
 
"100001"
,
  
"mac_address"
:
 
"00:1A:79:11:22:33"
,
  
"location_name"
:
 
"Entrance Gate"
,
  
"current_site"
:
 
"SITE1"
,
  
"current_ip"
:
 
"192.168.1.3"
,
  
"stream_status"
:
 
"active"
,
  
"created_at"
:
 
""
}
Stream Collection
{
  
"_id"
:
 
""
,
  
"camera_code"
:
 
"100001"
,
  
"stream_name"
:
 
"100001"
,
  
"hls_url"
:
 
"https://cloud/hls/100001/index.m3u8"
,
  
"status"
:
 
"active"
,
  
"last_seen"
:
 
""
}
Camera Migration History
{
  
"_id"
:
 
""
,
  
"camera_code"
:
 
"100001"
,
  
"old_site"
:
 
"SITE1"
,
  
"new_site"
:
 
"SITE2"
,
  
"moved_at"
:
 
""
}
5. Website Modules
Module 1: Authentication
Features
Login
Logout
JWT Authentication
Role-based access
Pages
/login
API
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/me
Module 2: Dashboard
Features
Display:
Total Sites
Total Cameras
Active Streams
Offline Streams
Users
Widgets
Total Sites
Total Cameras
Active Streams
Offline Streams
Recent Camera Movements
Route
/dashboard
Module 3: Site Management
Admin Functions
Create Site
Edit Site
Delete Site
View Site
Route
/sites
APIs
GET /api/sites
POST /api/sites
PUT /api/sites/{id}
DELETE /api/sites/{id}
Module 4: Camera Registration
Objective
Register camera before streaming.
Form
Camera Code
MAC Address
Location
Validation
Camera Code:
Exactly 6 digits
MAC Address:
Unique
Route
/cameras/register
APIs
POST /api/cameras
GET /api/cameras
GET /api/cameras/{id}
PUT /api/cameras/{id}
Module 5: Camera Location Assignment
Example
100001
→ Entrance Gate
100002
→ Water Tank
Features
Update location
Search by camera code
Search by site
Route
/cameras
Module 6: User Management
Features
Create User
Assign Sites
Reset Password
Disable User
Route
/users
APIs
POST /api/users
GET /api/users
PUT /api/users/{id}
DELETE /api/users/{id}
Module 7: Site Assignment
Example
User:
Security Officer
Assigned:
SITE1
SITE3
SITE5
Features
Multi-select sites.
Backend Logic
Store:
{
  
"assigned_sites"
:
 
[
    
"SITE1"
,
    
"SITE3"
  
]
}
Module 8: Live Stream Viewer
Core Module
Display streams grouped by Site.
Layout
SITE1
 Entrance Gate
 Water Tank
 Parking
SITE2
 Warehouse
 Main Road
Stream Player
Use:
HLS.js
Player Source:
https://cloud/hls/100001/index.m3u8
Route
/live
Module 9: Stream Control
Admin Only.
Actions
Pause Stream
Resume Stream
UI
[Play]
[Pause]
API
POST /api/streams/pause
POST /api/streams/resume
Database
{
  
"camera_code"
:
 
"100001"
,
  
"status"
:
 
"paused"
}
Module 10: Camera Movement Tracking
Purpose
Track camera migration between sites.
Example
100001
SITE1
→
SITE2
18-Jun-2026
Route
/camera-history
API
GET /api/camera-history
Module 11: Search System
Global Search.
Search By:
Camera Code
MAC Address
Location
Site
Route
/search
Module 12: Notifications
Display:
Camera Offline
Stream Offline
Camera Moved Site
Local Server Offline
Notification Center
/notifications
6. Frontend Pages
/login
/dashboard
/sites
/sites/:id
/cameras
/cameras/register
/users
/live
/camera-history
/notifications
/profile
7. UI Layout
Sidebar
Dashboard
Sites
Cameras
Users
Live Streams
Movement History
Notifications
Logout
Header
User Name
Role
Profile
Logout
8. API Integration Phase
Integrate Website With Cloud APIs.
Consume:
GET /api/sites
GET /api/cameras
GET /api/streams
GET /api/notifications
GET /api/users
9. Security
Implement:
JWT Authentication
Password Hashing
Route Protection
Role-Based Access
API Authorization
Secure Cookies
10. Development Phases
Phase 1
Authentication
Dashboard
Site Management
Duration:
1 Week
Phase 2
Camera Registration
Camera Management
Location Assignment
Duration:
1 Week
Phase 3
User Management
Site Assignment
Role System
Duration:
1 Week
Phase 4
Live Stream Viewer
HLS Integration
Site Grouping
Duration:
1 Week
Phase 5
Stream Control
Migration History
Notifications
Duration:
1 Week
11. Final Deliverables
Frontend:
React Application
HLS Stream Viewer
Responsive UI
Backend:
Flask REST API
JWT Security
MongoDB Integration
Features:
Camera Registration
User Management
Site Management
Stream Monitoring
HLS Viewing
Site-Based Permissions
Camera Migration Tracking
Stream Control
The website serves as the centralized control and monitoring layer for the complete multi-site camera streaming ecosystem.