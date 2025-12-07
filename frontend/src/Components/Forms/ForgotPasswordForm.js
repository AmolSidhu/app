import React, { useState } from "react";
import server from "../Static/Constants";

const ForgotPasswordForm = () => {
    const [email, setEmail] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage("");
        setError("");

        try {
            const response = await fetch(`${server}/forgot/password/`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message || "Password reset successfully. Check your email.");
            } else {
                setError(data.message || "Failed to reset password. Please try again.");
            }
        } catch (err) {
            console.error("Error during password reset request:", err);
            setError("Internal error. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>Forgot Password</h2>
            <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
            />
            <button type="submit" disabled={loading}>
                {loading ? "Processing..." : "Send New Password"}
            </button>
            {message && <p className="success">{message}</p>}
            {error && <p className="error">{error}</p>}
        </form>
    );
};

export default ForgotPasswordForm;