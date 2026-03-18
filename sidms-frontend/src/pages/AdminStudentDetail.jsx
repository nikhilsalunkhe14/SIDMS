import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./AdminDashboard.css";

function AdminStudentDetail() {
    const { studentId } = useParams();
    const [student, setStudent] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        fetchStudentDetail();
    }, [studentId]);

    // Refresh data when component becomes visible (when navigating back)
    useEffect(() => {
        const handleVisibilityChange = () => {
            if (!document.hidden) {
                fetchStudentDetail();
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
    }, [studentId]);

    const fetchStudentDetail = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:5000/api/admin/student/${studentId}`, {
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (response.ok) {
                const data = await response.json();
                setStudent(data.student);
            } else {
                setError("Failed to fetch student details");
            }
        } catch (err) {
            setError("Error connecting to server");
        } finally {
            setLoading(false);
        }
    };

    const handleBackToDashboard = () => {
        navigate("/admin-dashboard");
    };

    const handleArchiveStudent = async () => {
        if (!window.confirm("Are you sure you want to archive this student profile?\n\nThis will hide the profile from the active student list but preserve all data for audit purposes.")) {
            return;
        }

        try {
            const token = localStorage.getItem("token");
            // Use student.user_id instead of studentId (which is profile_id)
            const userId = student?.user_id;
            if (!userId) {
                alert("Student user ID not found");
                return;
            }
            
            const response = await fetch(`http://localhost:5000/api/admin/students/${userId}/archive`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (response.ok) {
                const data = await response.json();
                alert("Student profile archived successfully!");
                navigate("/admin-dashboard");
            } else {
                const errorData = await response.json();
                alert(`Failed to archive profile: ${errorData.message || "Unknown error"}`);
            }
        } catch (err) {
            alert("Error connecting to server");
        }
    };

    const handleRestoreStudent = async () => {
        if (!window.confirm("Are you sure you want to restore this student profile?\n\nThis will make the profile visible again in the active student list.")) {
            return;
        }

        try {
            const token = localStorage.getItem("token");
            // Use student.user_id instead of studentId (which is profile_id)
            const userId = student?.user_id;
            if (!userId) {
                alert("Student user ID not found");
                return;
            }
            
            const response = await fetch(`http://localhost:5000/api/admin/students/${userId}/restore`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (response.ok) {
                const data = await response.json();
                alert("Student profile restored successfully!");
                // Refresh the student data to show updated status
                fetchStudentDetail();
            } else {
                const errorData = await response.json();
                alert(`Failed to restore profile: ${errorData.message || "Unknown error"}`);
            }
        } catch (err) {
            alert("Error connecting to server");
        }
    };

    const maskSensitiveData = (data, type) => {
        if (!data || data === "Not set") return data;
        
        switch (type) {
            case 'phone':
                // Admin should see full phone number for management purposes
                return data; // Show full phone number to admin
            case 'student_id':
                // Admin should see full student ID for management purposes
                return data; // Show full student ID to admin
            default:
                return data;
        }
    };

    const handleExportData = async () => {
        try {
            const token = localStorage.getItem("token");
            const userId = student?.user_id;
            if (!userId) {
                alert("Student user ID not found");
                return;
            }
            
            const response = await fetch(`http://localhost:5000/api/admin/student/${userId}/export`, {
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (response.ok && response.headers.get('content-type')?.includes('application/pdf')) {
                // Create and download PDF file
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                // Get filename from Content-Disposition header or create default
                const contentDisposition = response.headers.get('content-disposition');
                let filename = `student_data_export_${student.full_name}_${new Date().toISOString().split('T')[0]}.pdf`;
                
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                    if (filenameMatch) {
                        filename = filenameMatch[1];
                    }
                }
                
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                alert("Student data exported successfully as PDF!");
            } else {
                const errorData = await response.json();
                alert(`Failed to export data: ${errorData.message || "Unknown error"}`);
            }
        } catch (err) {
            alert("Error connecting to server");
        }
    };

    const handleViewAuditLogs = async () => {
        try {
            const token = localStorage.getItem("token");
            const userId = student?.user_id;
            if (!userId) {
                alert("Student user ID not found");
                return;
            }
            
            const response = await fetch(`http://localhost:5000/api/admin/student/${userId}/audit-logs`, {
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (response.ok) {
                const data = await response.json();
                
                // Create a modal or navigate to audit logs page
                const logsText = data.logs.map(log => 
                    `${new Date(log.timestamp).toLocaleString()} - ${log.action}: ${log.details?.description || 'N/A'} (IP: ${log.ip_address || 'N/A'})`
                ).join('\n\n');
                
                alert(`Audit Logs (${data.total} entries):\n\n${logsText}`);
            } else {
                const errorData = await response.json();
                alert(`Failed to fetch audit logs: ${errorData.message || "Unknown error"}`);
            }
        } catch (err) {
            alert("Error connecting to server");
        }
    };

    if (loading) {
        return <div className="admin-dashboard-loading">Loading student details...</div>;
    }

    if (error) {
        return <div className="admin-dashboard-error">{error}</div>;
    }

    if (!student) {
        return <div className="admin-dashboard-error">Student not found</div>;
    }

    return (
        <div className="admin-dashboard">
            {/* Header */}
            <div className="admin-header">
                <div className="admin-header-content">
                    <div className="admin-title">
                        <button onClick={handleBackToDashboard} className="back-btn">
                            ← Back to Dashboard
                        </button>
                        <h1>Student Details</h1>
                        <p>View complete student profile information</p>
                    </div>
                </div>
            </div>

            {/* Student Detail Card */}
            <div className="admin-student-detail-container">
                <div className="admin-student-detail-card">
                    {/* Student Header */}
                    <div className="student-detail-header">
                        <div className="student-avatar-large">
                            {student.full_name?.charAt(0)?.toUpperCase() || 'S'}
                        </div>
                        <div className="student-basic-info">
                            <h2>{student.full_name || 'N/A'}</h2>
                            <p>{student.email || 'N/A'}</p>
                            <span className="student-role">Student</span>
                        </div>
                    </div>

                    {/* Contact Information */}
                    <div className="student-section">
                        <h3>📞 Contact Information</h3>
                        <div className="info-grid">
                            <div className="info-item">
                                <span className="info-label">Email:</span>
                                <span className="info-value">{student.email || 'Not provided'}</span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Phone:</span>
                                <span className="info-value">
                                    {maskSensitiveData(student.phone_number, 'phone')}
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">🏠 Residential Address:</span>
                                <span className="info-value">{student.residential_address || 'Not provided'}</span>
                            </div>
                        </div>
                    </div>

                    {/* Academic Information */}
                    <div className="student-section">
                        <h3>🎓 Academic Information</h3>
                        <div className="info-grid">
                            <div className="info-item">
                                <span className="info-label">🏫 College:</span>
                                <span className="info-value">{student.college_name || 'Not provided'}</span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Degree:</span>
                                <span className="info-value">{student.degree || 'Not provided'}</span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Student ID:</span>
                                <span className="info-value">
                                    {maskSensitiveData(student.student_id, 'student_id')}
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Resume:</span>
                                <span className="info-value">
                                    {student.resume_url ? 
                                        <a href={student.resume_url} target="_blank" rel="noopener noreferrer" className="resume-link">
                                            View Resume
                                        </a> : 
                                        'Not provided'
                                    }
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Resume Information */}
                    <div className="student-section">
                        <h3>📄 Resume</h3>
                        <div className="info-grid">
                            <div className="info-item">
                                <span className="info-label">Resume URL:</span>
                                <span className="info-value">
                                    {student.resume_url ? (
                                        <a href={student.resume_url} target="_blank" rel="noopener noreferrer" className="resume-link">
                                            View Resume →
                                        </a>
                                    ) : (
                                        'Not provided'
                                    )}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* System Information */}
                    <div className="student-section">
                        <h3>🔧 System Information</h3>
                        <div className="info-grid">
                            <div className="info-item">
                                <span className="info-label">User ID:</span>
                                <span className="info-value">{student.user_id || 'N/A'}</span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Profile Created:</span>
                                <span className="info-value">
                                    {student.created_at ? 
                                        new Date(student.created_at).toLocaleDateString() : 
                                        'N/A'
                                    }
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Last Updated:</span>
                                <span className="info-value">
                                    {student.updated_at ? 
                                        new Date(student.updated_at).toLocaleDateString() : 
                                        'N/A'
                                    }
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Security & Compliance Insights */}
                    <div className="student-section">
                        <h3>🔐 Security & Compliance Insights</h3>
                        <div className="info-grid">
                            <div className="info-item">
                                <span className="info-label">MFA Status:</span>
                                <span className="info-value">
                                    {student.user_info?.mfa_enabled ? (
                                        <span style={{ color: '#10b981' }}>✅ Enabled</span>
                                    ) : (
                                        <span style={{ color: '#ef4444' }}>❌ Disabled</span>
                                    )}
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Account Status:</span>
                                <span className="info-value">
                                    {student.user_info?.enabled ? (
                                        <span style={{ color: '#10b981' }}>✅ Active</span>
                                    ) : (
                                        <span style={{ color: '#ef4444' }}>❌ Disabled</span>
                                    )}
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">User Role:</span>
                                <span className="info-value">{student.user_info?.role || 'N/A'}</span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Username:</span>
                                <span className="info-value">{student.user_info?.username || 'N/A'}</span>
                            </div>
                        </div>
                    </div>

                    {/* Activity History */}
                    <div className="student-section">
                        <h3>📊 Activity History</h3>
                        <div className="info-grid">
                            <div className="info-item">
                                <span className="info-label">Account Created:</span>
                                <span className="info-value">
                                    {student.user_info?.user_created_at ? 
                                        new Date(student.user_info.user_created_at).toLocaleDateString() + ' ' + 
                                        new Date(student.user_info.user_created_at).toLocaleTimeString() : 
                                        'N/A'
                                    }
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Profile Created:</span>
                                <span className="info-value">
                                    {student.created_at ? 
                                        new Date(student.created_at).toLocaleDateString() + ' ' + 
                                        new Date(student.created_at).toLocaleTimeString() : 
                                        'N/A'
                                    }
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Last Updated:</span>
                                <span className="info-value">
                                    {student.updated_at ? 
                                        new Date(student.updated_at).toLocaleDateString() + ' ' + 
                                        new Date(student.updated_at).toLocaleTimeString() : 
                                        'N/A'
                                    }
                                </span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Account Updated:</span>
                                <span className="info-value">
                                    {student.user_info?.user_updated_at ? 
                                        new Date(student.user_info.user_updated_at).toLocaleDateString() + ' ' + 
                                        new Date(student.user_info.user_updated_at).toLocaleTimeString() : 
                                        'N/A'
                                    }
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                
                {/* Enhanced Action Buttons */}
                <div className="admin-actions">
                    <div className="action-group">
                        {student.status !== 'archived' ? (
                            <button 
                                className="archive-btn"
                                onClick={() => handleArchiveStudent()}
                            >
                                📦 Archive Profile
                            </button>
                        ) : (
                            <button 
                                className="restore-btn"
                                onClick={() => handleRestoreStudent()}
                            >
                                ♻️ Restore Profile
                            </button>
                        )}
                    </div>
                    <div className="action-group">
                        <button 
                            className="export-btn"
                            onClick={() => handleExportData()}
                        >
                            📤 Export Data (GDPR)
                        </button>
                        <button 
                            className="audit-btn"
                            onClick={() => handleViewAuditLogs()}
                        >
                            📋 View Audit Logs
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AdminStudentDetail;
