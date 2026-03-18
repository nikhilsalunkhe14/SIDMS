import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Register.css";

function Register() {
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage("");
        setMessageType("");

        if (password !== confirmPassword) {
            setMessage("Passwords do not match.");
            setMessageType("error");
            return;
        }

        setLoading(true);

        try {
            const response = await fetch("http://localhost:5000/api/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, username, password }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message || "Registration successful! Check your email to verify.");
                setMessageType("success");

                setTimeout(() => {
                    navigate("/login");
                }, 2500);
            } else {
                setMessage(data.message || "Registration failed. Please try again.");
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
            <div className="login-card register-card">
                {/* Brand */}
                <div className="login-brand">
                    <div className="login-brand-icon">📝</div>
                    <h1>Create Account</h1>
                    <p>Join SIDMS — Secure IAC Data Management</p>
                </div>

                {/* Form */}
                <form className="login-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="reg-email">Email</label>
                        <input
                            id="reg-email"
                            type="email"
                            placeholder="Enter your email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            autoComplete="email"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="reg-username">Username</label>
                        <input
                            id="reg-username"
                            type="text"
                            placeholder="Choose a username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            autoComplete="username"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="reg-password">Password</label>
                        <input
                            id="reg-password"
                            type="password"
                            placeholder="Create a password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            autoComplete="new-password"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="reg-confirm-password">Confirm Password</label>
                        <input
                            id="reg-confirm-password"
                            type="password"
                            placeholder="Confirm your password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            autoComplete="new-password"
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
                        {loading ? "Creating Account…" : "Register"}
                    </button>
                </form>

                {/* Link to Login */}
                <div className="register-footer">
                    Already have an account?{" "}
                    <Link to="/login" className="register-link">Sign In</Link>
                </div>
            </div>
        </div>
    );
}

export default Register;
