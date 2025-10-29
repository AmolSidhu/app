import React, { useEffect, useState } from "react";
import server from "../Static/Constants";
import { useLocation } from "react-router-dom";

const ViewScraperHistoryRequest = () => {
    const location = useLocation();
    const search = location.search;
    const [history, setHistory] = useState([]);
    const [errorMessage, setErrorMessage] = useState(null);
    const [loading, setLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState(null);

    const params = new URLSearchParams(search);
    const scraperSerial = params.get("serial");

    useEffect(() => {
        const fetchHistory = async () => {
            setLoading(true);
            setErrorMessage(null);
            try {
                if (!scraperSerial) {
                    setErrorMessage("Missing serial in query string.");
                    setLoading(false);
                    return;
                }

                const response = await fetch(
                    `${server}/get/scraper_status/${scraperSerial}/`,
                    {
                        method: "GET",
                        headers: {
                            Authorization: localStorage.getItem("token"),
                        },
                    }
                );

                if (!response.ok) {
                    const text = await response.text();
                    setErrorMessage("Server returned an error: " + text);
                    setLoading(false);
                    return;
                }

                const data = await response.json();
                console.log("Data from server:", data);

                const outputs = Object.entries(data.scraper_outputs || {}).map(
                    ([serial_output, details]) => ({
                        serial_output,
                        ...details,
                    })
                );
                setHistory(outputs);

                if (outputs.length === 0) {
                    setSuccessMessage("No scraper history found for this serial.");
                }
            } catch (err) {
                setErrorMessage("Error fetching history: " + err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [search, scraperSerial]);

    const handleDownload = async (serialOutput) => {
        try {
            const token = localStorage.getItem("token");
            const url = `${server}/download/scraper_output/${scraperSerial}/${serialOutput}/`;

            const response = await fetch(url, {
                method: "GET",
                headers: {
                    Authorization: token,
                },
            });

            if (!response.ok) {
                const text = await response.text();
                setErrorMessage("Download failed: " + text);
                return;
            }

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = downloadUrl;

            const contentDisposition = response.headers.get("Content-Disposition");
            const match = contentDisposition?.match(/filename="?([^"]+)"?/);
            link.download = match ? match[1] : `scraper_output_${serialOutput}.csv`;

            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(downloadUrl);
        } catch (err) {
            setErrorMessage("Error during download: " + err.message);
        }
    };

    return (
        <div style={{ padding: "20px" }}>
            <h2>Scraper History</h2>

            {loading && <p>Loading...</p>}
            {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

            {history.length > 0 && (
                <table
                    style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        marginTop: "10px",
                    }}
                >
                    <thead>
                        <tr>
                            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "8px" }}>File Name</th>
                            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "8px" }}>Status</th>
                            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "8px" }}>Run Number</th>
                            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "8px" }}>Created</th>
                            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "8px" }}>Updated</th>
                            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "8px" }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history.map((item, index) => (
                            <tr key={index}>
                                <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>{item.file_name}</td>
                                <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>{item.status}</td>
                                <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>{item.run_number}</td>
                                <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>{item.create_date}</td>
                                <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>{item.update_date}</td>
                                <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>
                                    <button
                                        onClick={() => handleDownload(item.serial_output)}
                                        style={{
                                            backgroundColor: "#007bff",
                                            color: "white",
                                            border: "none",
                                            borderRadius: "5px",
                                            padding: "6px 12px",
                                            cursor: "pointer",
                                        }}
                                    >
                                        Download
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default ViewScraperHistoryRequest;