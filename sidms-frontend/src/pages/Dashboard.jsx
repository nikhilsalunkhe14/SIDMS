import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { get } from "../utils/apiClient";
import "./Dashboard.css";

// Helper function to mask sensitive data (only for admin role)
const maskSensitiveData = (data, type = 'default', isAdmin = false) => {
    if (!data || data === "Not set") return data;
    
    // Only mask if user is admin
    if (!isAdmin) {
        return data; // Show full data to students
    }
    
    // Auto-detect Aadhaar number (12 digits)
    if (type === 'government_id' && /^\d{12}$/.test(data)) {
        type = 'aadhaar';
    }
    
    switch (type) {
        case 'aadhaar':
            // Show last 4 digits for Aadhaar (12 digits)
            if (data.length >= 4) {
                return 'XXXX-XXXX-' + data.slice(-4);
            }
            return 'XXXX-XXXX-XXXX';
        case 'phone':
            // Show last 4 digits for phone numbers
            if (data.length >= 4) {
                return 'XXX-XXX-' + data.slice(-4);
            }
            return 'XXX-XXX-XXXX';
        case 'government_id':
            // Show last 4 digits for any government ID
            if (data.length >= 4) {
                return 'XXXX-XXXX-' + data.slice(-4);
            }
            return 'XXXX-XXXX-XXXX';
        default:
            return data;
    }
};

function Dashboard() {
    const navigate = useNavigate();
    const { username, role, token, logout } = useAuth();
    const [profileLoaded, setProfileLoaded] = useState(false);
    const [checking, setChecking] = useState(true);
    const [profileData, setProfileData] = useState(null); // New state for profile data

    /** Decode the JWT payload to extract extra claims (role, exp, etc.) */
    const decodeToken = () => {
        if (!token) return null;
        try {
            const payload = token.split(".")[1];
            return JSON.parse(atob(payload));
        } catch {
            return null;
        }
    };

    const decoded = decodeToken();

    // Prefer decoded role from JWT, fall back to context role
    const displayRole = decoded?.role || decoded?.authorities || role || "User";
    const displayUsername = decoded?.sub || username || "User";
    const isAdmin = displayRole === "ROLE_ADMIN"; // Check if user is admin

    // Check if profile exists and fetch profile data on load
    useEffect(() => {
        const checkProfile = async () => {
            try {
                const response = await get("/api/members/me");

                if (response.ok) {
                    const data = await response.json();
                    setProfileData(data.profile); // Store profile data
                    setProfileLoaded(true);
                } else if (response.status === 404) {
                    // No profile — redirect to complete profile
                    navigate("/complete-profile", { replace: true });
                    return;
                }
            } catch {
                // Network error — still show dashboard
                setProfileLoaded(true);
            } finally {
                setChecking(false);
            }
        };

        checkProfile();
    }, [navigate]);

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    // Show loading while checking profile
    if (checking) {
        return (
            <div className="dashboard-page">
                <nav className="dashboard-navbar">
                    <div className="dashboard-navbar-brand">
                        <div className="dashboard-navbar-logo">🔐</div>
                        <span>SIDMS</span>
                    </div>
                </nav>
                <main className="dashboard-content">
                    <div className="dashboard-welcome-card">
                        <div className="dashboard-welcome-icon">⏳</div>
                        <h1>Loading…</h1>
                        <p>Checking your profile status.</p>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className="dashboard-page">
            {/* ── Navbar ──────────────────────────────── */}
            <nav className="dashboard-navbar">
                <div className="dashboard-navbar-brand">
                    <div className="dashboard-navbar-logo">🔐</div>
                    <span>SIDMS</span>
                </div>
                <div className="dashboard-navbar-actions">
                    <span className="dashboard-role-badge">{displayRole}</span>
                    <button className="dashboard-logout-btn" onClick={handleLogout}>
                        Sign Out
                    </button>
                </div>
            </nav>

            {/* ── Main Content ───────────────────────── */}
            <main className="dashboard-content">
                <div className="dashboard-welcome-card">
                    <div className="dashboard-welcome-icon">👋</div>
                    <h1>Welcome, {profileData?.full_name || displayUsername}!</h1>
                    <p>
                        You are signed in to the Secure IAC Data Management System.
                        Your session is active and authenticated.
                    </p>

                    {/* Profile Info Grid */}
                    <div className="dashboard-info-grid">
                        <div className="dashboard-info-item">
                            <div className="dashboard-info-label">Full Name</div>
                            <div className="dashboard-info-value">{profileData?.full_name || "Not set"}</div>
                        </div>
                        <div className="dashboard-info-item">
                            <div className="dashboard-info-label">Email</div>
                            <div className="dashboard-info-value">{profileData?.email || "Not set"}</div>
                        </div>
                        <div className="dashboard-info-item">
                            <div className="dashboard-info-label">Phone Number</div>
                            <div className="dashboard-info-value">
                                {maskSensitiveData(profileData?.phone_number, 'phone', isAdmin)}
                                {isAdmin && profileData?.phone_number && profileData?.phone_number !== "Not set" && (
                                    <span style={{ color: '#999', fontSize: '12px', marginLeft: '5px' }}>🔒</span>
                                )}
                            </div>
                        </div>
                        <div className="dashboard-info-item">
                            <div className="dashboard-info-label">College</div>
                            <div className="dashboard-info-value">{profileData?.address || "Not set"}</div>
                        </div>
                        <div className="dashboard-info-item">
                            <div className="dashboard-info-label">Degree</div>
                            <div className="dashboard-info-value">{profileData?.degree || "Not set"}</div>
                        </div>
                        <div className="dashboard-info-item">
                            <div className="dashboard-info-label">Resume</div>
                            <div className="dashboard-info-value">
                                {profileData?.resume_url ? (
                                    <div>
                                        <a 
                                            href={profileData.resume_url} 
                                            target="_blank" 
                                            rel="noopener noreferrer" 
                                            style={{ 
                                                color: '#007bff', 
                                                textDecoration: 'none',
                                                fontWeight: '500',
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '5px'
                                            }}
                                        >
                                            📄 View Resume
                                        </a>
                                        <div style={{ marginTop: '5px' }}>
                                            <small style={{ color: '#666', fontSize: '11px', wordBreak: 'break-all' }}>
                                                {profileData.resume_url}
                                            </small>
                                        </div>
                                    </div>
                                ) : (
                                    <span style={{ color: '#999' }}>No resume provided</span>
                                )}
                            </div>
                        </div>
                        <div className="dashboard-info-item">
                            <div className="dashboard-info-label">Student ID</div>
                            <div className="dashboard-info-value">
                                {profileData?.student_id ? (
                                    <>
                                        {maskSensitiveData(profileData.student_id, 'student_id', isAdmin)}
                                        {isAdmin && (
                                            <span style={{ color: '#999', fontSize: '12px', marginLeft: '5px' }}>🔒</span>
                                        )}
                                    </>
                                ) : (
                                    <span style={{ color: '#999' }}>Not provided</span>
                                )}
                            </div>
                        </div>
                        <div className="dashboard-info-item">
                            <div className="dashboard-info-label">Username</div>
                            <div className="dashboard-info-value">{displayUsername}</div>
                        </div>
                        <div className="dashboard-info-item">
                            <div className="dashboard-info-label">Role</div>
                            <div className="dashboard-info-value">{displayRole}</div>
                        </div>
                        {profileData?.created_at && (
                            <div className="dashboard-info-item" style={{ gridColumn: "1 / -1" }}>
                                <div className="dashboard-info-label">Profile Created</div>
                                <div className="dashboard-info-value">
                                    {new Date(profileData.created_at).toLocaleString()}
                                </div>
                            </div>
                        )}
                        
                        {/* Edit Profile Section */}
                        <div className="dashboard-edit-section" style={{ gridColumn: "1 / -1" }}>
                            <button 
                                className="dashboard-edit-btn"
                                onClick={() => navigate("/profile")}
                            >
                                ✏️ Edit Profile
                            </button>
                            <small style={{ color: '#94a3b8', fontSize: '12px', display: 'block', marginTop: '8px', textAlign: 'center' }}>
                                Update your personal information, contact details, and resume
                            </small>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default Dashboard;
