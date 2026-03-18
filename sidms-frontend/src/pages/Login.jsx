import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Login.css";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState(""); // "success" | "error"
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage("");
        setMessageType("");
        setLoading(true);

        try {
            const response = await fetch("http://localhost:5000/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (response.ok) {
                // Check if admin login (direct token)
                if (data.token) {
                    // Admin login - use AuthContext login method
                    login({
                        token: data.token,
                        role: data.user.role,
                        username: data.user.username
                    });
                    
                    setMessage("Admin login successful!");
                    setMessageType("success");
                    
                    setTimeout(() => {
                        navigate("/admin-dashboard");
                    }, 1000);
                } else {
                    // Regular user - OTP flow
                    setMessage(data.message || "OTP sent to your registered email.");
                    setMessageType("success");

                    // Redirect to OTP verification after a brief delay so user sees the message
                    setTimeout(() => {
                        navigate("/otp", { state: { username } });
                    }, 1500);
                }
            } else {
                setMessage(data.message || "Invalid credentials. Please try again.");
                setMessageType("error");
            }
        } catch {
            setMessage("Unable to reach the server. Please try again later.");
            setMessageType("error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-card">
                {/* Brand */}
                <div className="login-brand">
                    <div className="login-brand-icon">🔐</div>
                    <h1>SIDMS</h1>
                    <p>Secure IAC Data Management System</p>
                </div>

                {/* Form */}
                <form className="login-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            id="username"
                            type="text"
                            placeholder="Enter your username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            autoComplete="username"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            autoComplete="current-password"
                        />
                    </div>

                    {/* Message */}
                    {message && (
                        <div className={`login-message ${messageType}`}>{message}</div>
                    )}

                    <button
                        type="submit"
                        className="login-btn"
                        disabled={loading}
                    >
                        {loading ? "Signing in…" : "Sign In"}
                    </button>
                </form>

                {/* Link to Register */}
                <div className="register-footer">
                    Don't have an account?{" "}
                    <Link to="/register" className="register-link">Sign Up</Link>
                </div>
            </div>
        </div>
    );
}

export default Login;
