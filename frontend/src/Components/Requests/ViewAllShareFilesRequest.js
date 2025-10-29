import React, { useEffect, useState } from "react";
import server from "../Static/Constants";
import UploadShareFilePopup from "../Popups/UploadShareFilePopup";

const ViewAllShareFilesRequest = () => {
    const [files, setFiles] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showUploadPopup, setShowUploadPopup] = useState(false);

    const fetchFiles = async () => {
        try {
            const response = await fetch(`${server}/get/files/`, {
                method: "GET",
                headers: {
                    "Authorization": localStorage.getItem("token"),
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Error fetching files");
            }
            setFiles(data.data || {});
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const updateShareStatus = async (fileId, newStatus) => {
        try {
            const response = await fetch(`${server}/update/file_share_status/${fileId}/`, {
                method: "PATCH",
                headers: {
                    "Authorization": localStorage.getItem("token"),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ sharable: newStatus })
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Error updating status");
            }

            fetchFiles();
        } catch (err) {
            alert(`Failed to update status: ${err.message}`);
        }
    };

    const copyShareLink = async (fileId) => {
        try {
            const response = await fetch(`${server}/get/file_share_link/${fileId}/`, {
                method: "GET",
                headers: {
                    "Authorization": localStorage.getItem("token"),
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Error fetching share link");
            }

            const link = `${window.location.origin}/files/sharefile/?serial=${data.data.serial}&share_code=${data.data.share_code}`;
            await navigator.clipboard.writeText(link);
            alert("Share link copied to clipboard!");
        } catch (err) {
            alert(`Failed to copy link: ${err.message}`);
        }
    };

    useEffect(() => {
        fetchFiles();
    }, []);

    if (loading) return <p>Loading files...</p>;
    if (error) return <p>Error: {error}</p>;
    if (Object.keys(files).length === 0 && !showUploadPopup) {
        return (
            <div>
                <p>No files found</p>
                <button onClick={() => setShowUploadPopup(true)}>Upload File</button>
                {showUploadPopup && (
                    <UploadShareFilePopup
                        onClose={() => setShowUploadPopup(false)}
                        onUploadSuccess={fetchFiles}
                    />
                )}
            </div>
        );
    }

    return (
        <div className="view-all-share-files-request">
            <h2>View All Shared Files</h2>
            <button onClick={() => setShowUploadPopup(true)}>Upload New File</button>
            <ul>
                {Object.entries(files).map(([serial, file]) => (
                    <li key={serial}>
                        <strong>{file.file_name}</strong> - {file.file_description} ({file.file_type})
                        <br />

                        <label>
                            <input
                                type="checkbox"
                                checked={file.file_share_status}
                                onChange={(e) => updateShareStatus(serial, e.target.checked)}
                            />
                            Sharable
                        </label>

                        <button
                            onClick={() => copyShareLink(serial)}
                            disabled={!file.file_share_status}
                            style={{ marginLeft: "10px" }}
                        >
                            Copy Share Link
                        </button>
                    </li>
                ))}
            </ul>

            {showUploadPopup && (
                <UploadShareFilePopup
                    onClose={() => setShowUploadPopup(false)}
                    onUploadSuccess={fetchFiles}
                />
            )}
        </div>
    );
};

export default ViewAllShareFilesRequest;