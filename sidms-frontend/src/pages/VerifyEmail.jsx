import { useState, useEffect } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import "./VerifyEmail.css";

function VerifyEmail() {
    const [searchParams] = useSearchParams();
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState(""); // "success" | "error"
    const [verifying, setVerifying] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const user_id = searchParams.get("user_id");

        if (!user_id) {
            setMessage("Invalid verification link. No user ID provided.");
            setMessageType("error");
            setVerifying(false);
            return;
        }

        const verify = async () => {
            try {
                const response = await fetch(
                    "http://localhost:5000/api/auth/verify-email",
                    {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ user_id }),
                    }
                );

                const data = await response.json();

                if (response.ok) {
                    setMessage(data.message || "Email verified successfully!");
                    setMessageType("success");

                    setTimeout(() => {
                        navigate("/login");
                    }, 3000);
                } else {
                    setMessage(data.message || "Verification failed. The link may be invalid or expired.");
                    setMessageType("error");
                }
            } catch (error) {
                console.error("Verification error:", error);
                setMessage("Unable to reach the server. Please try again later.");
                setMessageType("error");
            } finally {
                setVerifying(false);
            }
        };

        verify();
    }, [searchParams, navigate]);

    return (
        <div className="login-page">
            <div className="login-card verify-card">
                <div className="login-brand">
                    <div className="login-brand-icon">
                        {verifying ? "⏳" : messageType === "success" ? "✅" : "❌"}
                    </div>
                    <h1>Email Verification</h1>
                    <p>
                        {verifying
                            ? "Verifying your email address…"
                            : messageType === "success"
                                ? "Redirecting to login in 3 seconds…"
                                : "Verification could not be completed"}
                    </p>
                </div>

                {/* Status Message */}
                {message && (
                    <div className={`login-message ${messageType}`}>{message}</div>
                )}

                {/* Back to Login link (shown on error) */}
                {!verifying && messageType === "error" && (
                    <div className="verify-footer">
                        <Link to="/login" className="register-link">← Back to Login</Link>
                    </div>
                )}
            </div>
        </div>
    );
}

export default VerifyEmail;
