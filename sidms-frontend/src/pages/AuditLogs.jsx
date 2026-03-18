import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminDashboard.css";

function AuditLogs() {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [filter, setFilter] = useState("");
    const [actionFilter, setActionFilter] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        fetchAuditLogs();
    }, []);

    const fetchAuditLogs = async () => {
        try {
            const token = localStorage.getItem("token");
            console.log("DEBUG: Token from localStorage:", token ? `${token.substring(0, 20)}...` : "No token found");
            
            const queryParams = new URLSearchParams({
                limit: "100",
                action: actionFilter,
                user_id: filter
            }).toString();
            
            const headers = {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            };
            console.log("DEBUG: Request headers:", headers);
            
            const response = await fetch(`http://localhost:5000/api/admin/audit-logs?${queryParams}`, {
                headers: headers,
            });

            console.log("DEBUG: Response status:", response.status);
            console.log("DEBUG: Response headers:", response.headers);

            if (response.ok) {
                const data = await response.json();
                console.log("DEBUG: Response data:", data);
                setLogs(data.logs || []);
            } else {
                const errorData = await response.json();
                console.log("DEBUG: Error response:", errorData);
                setError(errorData.message || "Failed to fetch audit logs");
            }
        } catch (err) {
            console.error("DEBUG: Fetch error:", err);
            setError("Error connecting to server");
        } finally {
            setLoading(false);
        }
    };

    const handleBackToDashboard = () => {
        navigate("/admin-dashboard");
    };

    const filteredLogs = logs.filter(log => 
        log.action?.toLowerCase().includes(actionFilter.toLowerCase()) ||
        log.user_id?.toLowerCase().includes(filter.toLowerCase()) ||
        JSON.stringify(log.details).toLowerCase().includes(filter.toLowerCase())
    );

    const getDisplayUser = (log) => {
        // If user_name is available, show it, otherwise show user_id
        return log.user_name || log.user_id || 'Unknown';
    };

    const getActionIcon = (action) => {
        switch (action) {
            case 'PROFILE_VIEW': return '👁';
            case 'PROFILE_UPDATE': return '✏️';
            case 'PROFILE_CREATE': return '➕';
            case 'LOGIN_SUCCESS': return '✅';
            case 'LOGIN_FAILED': return '❌';
            case 'ADMIN_ARCHIVED': return '📦';
            case 'ADMIN_RESTORED': return '♻️';
            case 'ADMIN_VIEWED_STUDENT_PROFILE': return '👤';
            default: return '📋';
        }
    };

    const getActionColor = (action) => {
        switch (action) {
            case 'PROFILE_VIEW': return '#6366f1';
            case 'PROFILE_UPDATE': return '#8b5cf6';
            case 'PROFILE_CREATE': return '#10b981';
            case 'LOGIN_SUCCESS': return '#10b981';
            case 'LOGIN_FAILED': return '#ef4444';
            case 'ADMIN_ARCHIVED': return '#f59e0b';
            case 'ADMIN_RESTORED': return '#10b981';
            case 'ADMIN_VIEWED_STUDENT_PROFILE': return '#3b82f6';
            default: return '#6b7280';
        }
    };

    if (loading) {
        return <div className="admin-dashboard-loading">Loading audit logs...</div>;
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
                        <h1>📊 Audit Logs</h1>
                        <p>SIDMS - Security & Compliance Dashboard</p>
                    </div>
                    <div className="admin-header-actions">
                        <button className="refresh-btn" onClick={fetchAuditLogs} title="Refresh logs">
                            🔄 Refresh
                        </button>
                        <button className="logout-btn" onClick={handleBackToDashboard}>
                            ← Back to Dashboard
                        </button>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="admin-search-section">
                <div className="admin-search-container">
                    <input
                        type="text"
                        placeholder="🔍 Filter by user ID..."
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="admin-search-input"
                    />
                    <input
                        type="text"
                        placeholder="🔍 Filter by action..."
                        value={actionFilter}
                        onChange={(e) => setActionFilter(e.target.value)}
                        className="admin-search-input"
                    />
                    <div className="admin-stats">
                        <span>Total Logs: {logs.length}</span>
                        <span>Filtered: {filteredLogs.length}</span>
                    </div>
                </div>
            </div>

            {/* Logs Table */}
            <div className="audit-logs-container">
                {filteredLogs.length === 0 ? (
                    <div className="admin-no-students">
                        {filter || actionFilter ? "No logs found matching your filters." : "No audit logs available."}
                    </div>
                ) : (
                    <div className="audit-logs-table">
                        <div className="audit-table-header">
                            <div>Time</div>
                            <div>User</div>
                            <div>Action</div>
                            <div>Details</div>
                            <div>IP Address</div>
                        </div>
                        {filteredLogs.map((log, index) => (
                            <div key={log.id} className={`audit-table-row ${index % 2 === 0 ? 'even' : 'odd'}`}>
                                <div className="audit-time">{log.formatted_time}</div>
                                <div className="audit-user">{getDisplayUser(log)}</div>
                                <div className="audit-action" style={{ color: getActionColor(log.action) }}>
                                    {getActionIcon(log.action)} {log.action}
                                </div>
                                <div className="audit-details">
                                    {log.details ? (
                                        <div className="audit-details-content">
                                            {typeof log.details === 'string' ? log.details : 
                                             Object.entries(log.details).map(([key, value]) => (
                                                <div key={key} className="detail-item">
                                                    <strong>{key}:</strong> {typeof value === 'object' ? JSON.stringify(value) : value}
                                                </div>
                                            ))
                                            }
                                        </div>
                                    ) : 'N/A'}
                                </div>
                                <div className="audit-ip">{log.ip_address || 'N/A'}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default AuditLogs;
