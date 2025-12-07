import React, { useEffect, useState } from "react";
import server from "../Static/Constants";

const ServerDataPopup = ({ onClose }) => {
    const [metadata, setMetadata] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchServerMetadata = async () => {
        const token = localStorage.getItem("token");
        try {
            const response = await fetch(`${server}/get/server/metadata/`, {
                headers: {
                    Authorization: token,
                },
            });
            const result = await response.json();

            if (response.ok) {
                setMetadata(result.data);
            } else {
                setError(result.message || "Failed to fetch server metadata.");
            }
        } catch (err) {
            console.error("Error fetching server metadata:", err);
            setError("Internal error. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchServerMetadata();
    }, []);

    if (loading) return <div className="server-data-popup">Loading...</div>;

    return (
        <div className="server-data-popup p-4 rounded-xl shadow-lg bg-white w-96">
            <button
                className="mb-4 text-sm bg-red-500 text-white px-3 py-1 rounded"
                onClick={onClose}
            >
                Close
            </button>

            {error ? (
                <p className="text-red-600">{error}</p>
            ) : (
                metadata && (
                    <div>
                        <h2 className="text-lg font-semibold mb-2">Server Metadata</h2>
                        <ul className="text-sm text-gray-700 space-y-1">
                            <li><strong>Version:</strong> {metadata.version}</li>
                            <li><strong>Environment:</strong> {metadata.enviroment}</li>
                            <li><strong>Database:</strong> {metadata.database}</li>
                            <li><strong>Selenium Driver:</strong> {metadata.selenium_driver_version}</li>
                            <li><strong>Last Updated:</strong> {metadata.last_updated}</li>
                            <li>
                                <strong>Other Requirements:</strong>{" "}
                                {metadata.other_requirements?.join(", ")}
                            </li>
                        </ul>
                    </div>
                )
            )}
        </div>
    );
};

export default ServerDataPopup;