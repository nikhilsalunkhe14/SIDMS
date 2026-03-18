import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Login.css";
import "./OtpVerification.css";

function OtpVerification() {
    const location = useLocation();
    const navigate = useNavigate();
    const { login } = useAuth();
    const username = location.state?.username || "";

    const [otp, setOtp] = useState("");
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState(""); // "success" | "error"
    const [loading, setLoading] = useState(false);

    // If someone navigates here directly without a username, send them back
    if (!username) {
        return (
            <div className="login-page">
                <div className="login-card">
                    <div className="login-brand">
                        <div className="login-brand-icon">⚠️</div>
                        <h1>Session Expired</h1>
                        <p>Please log in again to receive a new OTP.</p>
                    </div>
                    <button className="login-btn" onClick={() => navigate("/login")}>
                        Back to Login
                    </button>
                </div>
            </div>
        );
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage("");
        setMessageType("");
        setLoading(true);

        try {
            const response = await fetch("http://localhost:5000/api/auth/verify-otp", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, otp }),
            });

            const data = await response.json();

            if (response.ok) {
                // Store auth data via AuthContext
                login(data);

                setMessage("Verification successful! Redirecting to Profile Form…");
                setMessageType("success");

                setTimeout(() => {
                    navigate("/profileform");
                }, 1200);
            } else {
                setMessage(data.message || "Invalid OTP. Please try again.");
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
                    <div className="login-brand-icon">🔑</div>
                    <h1>OTP Verification</h1>
                    <p>Enter the OTP sent to the email for <strong>{username}</strong></p>
                </div>

                {/* Form */}
                <form className="login-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="otp">One-Time Password</label>
                        <input
                            id="otp"
                            type="text"
                            inputMode="numeric"
                            placeholder="Enter OTP"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            required
                            autoComplete="one-time-code"
                            className="otp-input"
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
                        {loading ? "Verifying…" : "Verify OTP"}
                    </button>

                    <button
                        type="button"
                        className="login-btn otp-back-btn"
                        onClick={() => navigate("/login")}
                    >
                        ← Back to Login
                    </button>
                </form>
            </div>
        </div>
    );
}

export default OtpVerification;
