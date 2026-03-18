import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminDashboard.css";

function AdminDashboard() {
    const [error, setError] = useState("");
    const [searchTerm, setSearchTerm] = useState("");
    const [showArchived, setShowArchived] = useState(false);
    const [loading, setLoading] = useState(true);
    const [students, setStudents] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchStudents();
    }, []);

    // Refresh data when component becomes visible (when navigating back)
    useEffect(() => {
        const handleVisibilityChange = () => {
            if (!document.hidden && !showArchived) {
                fetchStudents();
            } else if (!document.hidden && showArchived) {
                fetchArchivedStudents();
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
    }, [showArchived]);

    const fetchStudents = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch("http://localhost:5000/api/admin/students", {
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (response.ok) {
                const data = await response.json();
                setStudents(data.students || []);
            } else {
                setError("Failed to fetch students");
            }
        } catch (err) {
            setError("Error connecting to server");
        } finally {
            setLoading(false);
        }
    };

    const fetchArchivedStudents = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch("http://localhost:5000/api/admin/students/archived", {
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });

            if (response.ok) {
                const data = await response.json();
                setStudents(data.students || []);
            } else {
                setError("Failed to fetch archived students");
            }
        } catch (err) {
            setError("Error connecting to server");
        } finally {
            setLoading(false);
        }
    };

    const toggleView = () => {
        const newShowArchived = !showArchived;
        setShowArchived(newShowArchived);
        setLoading(true);
        if (newShowArchived) {
            fetchArchivedStudents();
        } else {
            fetchStudents();
        }
    };

    const filteredStudents = students.filter(student => 
        student.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.college?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleStudentClick = (studentId) => {
        navigate(`/admin/student/${studentId}`);
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/login");
    };

    const handleRefresh = () => {
        setLoading(true);
        if (showArchived) {
            fetchArchivedStudents();
        } else {
            fetchStudents();
        }
    };

    const handleViewAuditLogs = () => {
        navigate("/admin/audit-logs");
    };

    if (loading) {
        return <div className="admin-dashboard-loading">Loading...</div>;
    }

    if (error) {
        return <div className="admin-dashboard-error">{error}</div>;
    }

    return (
        <div className="admin-dashboard">
            {/* Header */}
            <div className="admin-header">
                <div className="admin-header-content">
                    <div className="admin-title">
                        <h1>🔐 Admin Dashboard</h1>
                        <p>SIDMS - Secure IAC Data Management System</p>
                    </div>
                    <div className="admin-header-actions">
                        <button className="refresh-btn" onClick={handleRefresh} title="Refresh data">
                            🔄 Refresh
                        </button>
                        <button className="audit-logs-btn" onClick={handleViewAuditLogs} title="View audit logs">
                            📊 Audit Logs
                        </button>
                        <button className="logout-btn" onClick={handleLogout}>
                            Logout
                        </button>
                    </div>
                </div>
            </div>

            {/* Search Section */}
            <div className="admin-search-section">
                <div className="admin-search-container">
                    <input
                        type="text"
                        placeholder="🔍 Search students by name, email, or college..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="admin-search-input"
                    />
                    <div className="admin-stats">
                        <span>Total Students: {students.length}</span>
                        <span>Filtered: {filteredStudents.length}</span>
                    </div>
                </div>
                
                {/* View Toggle */}
                <div className="admin-view-toggle">
                    <button 
                        className={`toggle-btn ${!showArchived ? 'active' : ''}`}
                        onClick={() => !showArchived || toggleView()}
                    >
                        👥 Active Students
                    </button>
                    <button 
                        className={`toggle-btn ${showArchived ? 'active' : ''}`}
                        onClick={() => showArchived || toggleView()}
                    >
                        📦 Archived Students
                    </button>
                </div>
            </div>

            {/* Students Grid */}
            <div className="admin-students-grid">
                {filteredStudents.length === 0 ? (
                    <div className="admin-no-students">
                        {searchTerm ? "No students found matching your search." : "No students registered yet."}
                    </div>
                ) : (
                    filteredStudents.map((student) => (
                        <div 
                            key={student.id} 
                            className="admin-student-card"
                            onClick={() => handleStudentClick(student.id)}
                        >
                            <div className="student-card-header">
                                <div className="student-avatar">
                                    {student.full_name?.charAt(0)?.toUpperCase() || 'S'}
                                </div>
                                <div className="student-info">
                                    <h3>{student.full_name || 'N/A'}</h3>
                                    <p>{student.email || 'N/A'}</p>
                                </div>
                            </div>
                            
                            <div className="student-details">
                                <div className="detail-item">
                                    <span className="detail-label">📱 Phone:</span>
                                    <span className="detail-value">
                                        {student.phone_number ? 
                                            `XXX-XXX-${student.phone_number.slice(-4)}` : 
                                            'Not provided'
                                        }
                                    </span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">� Address:</span>
                                    <span className="detail-value">{student.residential_address || 'Not provided'}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">🏫 College:</span>
                                    <span className="detail-value">{student.college_name || 'Not provided'}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">🆔 Student ID:</span>
                                    <span className="detail-value">
                                        {student.student_id || 'Not provided'}
                                    </span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">📄 Resume:</span>
                                    <span className="detail-value">
                                        {student.resume_url ? 
                                            <a href={student.resume_url} target="_blank" rel="noopener noreferrer" className="resume-link">
                                                View Resume
                                            </a> : 
                                            'Not provided'
                                        }
                                    </span>
                                </div>
                            </div>
                            
                            <div className="student-card-footer">
                                <span className="view-details-btn">View Full Details →</span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default AdminDashboard;
