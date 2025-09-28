import React, { useEffect, useState } from "react";
import server from "../Static/Constants";
import { useLocation } from "react-router-dom";
import UploadShareFilePopup from "../Popups/UploadShareFilePopup";

const ViewAllShareFolderFilesRequest = () => {
    const [files, setFiles] = useState([]);
    const [folderData, setFolderData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showPopup, setShowPopup] = useState(false);

    const location = useLocation();
    const search = location.search;
    const params = new URLSearchParams(search);
    const folderSerial = params.get("serial");

    const fetchFolderData = async () => {
        try {
            const response = await fetch(`${server}/get/folder_data/${folderSerial}/`, {
                method: "GET",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Error fetching folder data");
            }

            setFolderData(data.data);
        } catch (err) {
            setError(err.message);
        }
    };

    const fetchFiles = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${server}/get/folder_files/${folderSerial}/`, {
                method: "GET",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || "Error fetching files");
            }

            if (result.data) {
                const fileArray = Object.entries(result.data).map(([serial, file]) => ({
                    file_serial: serial,
                    ...file,
                }));
                setFiles(fileArray);
            } else {
                setFiles([]);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const updateFolderShareStatus = async (newStatus) => {
        try {
            const response = await fetch(`${server}/update/folder_share_status/${folderSerial}/`, {
                method: "PATCH",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ sharable: newStatus }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Error updating folder status");
            }

            fetchFolderData();
        } catch (err) {
            alert(`Failed to update folder sharable status: ${err.message}`);
        }
    };

    const copyFolderShareLink = async () => {
        try {
            const response = await fetch(`${server}/get/folder_share_link/${folderSerial}/`, {
                method: "GET",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Error fetching folder share link");
            }

            const link = `${window.location.origin}/files/share_folder/?serial=${data.data.serial}&share_code=${data.data.share_code}`;
            await navigator.clipboard.writeText(link);
            alert("Folder share link copied to clipboard!");
        } catch (err) {
            alert(`Failed to copy folder link: ${err.message}`);
        }
    };

    const updateFileShareStatus = async (fileId, newStatus) => {
        try {
            const response = await fetch(`${server}/update/file_share_status/${fileId}/`, {
                method: "PATCH",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ sharable: newStatus }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Error updating file status");
            }

            fetchFiles();
        } catch (err) {
            alert(`Failed to update file status: ${err.message}`);
        }
    };

    const copyFileShareLink = async (fileId) => {
        try {
            const response = await fetch(`${server}/get/file_share_link/${fileId}/`, {
                method: "GET",
                headers: {
                    Authorization: localStorage.getItem("token"),
                    "Content-Type": "application/json",
                },
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Error fetching file share link");
            }

            const link = `${window.location.origin}/files/share_file/?serial=${data.data.serial}&share_code=${data.data.share_code}`;
            await navigator.clipboard.writeText(link);
            alert("File share link copied to clipboard!");
        } catch (err) {
            alert(`Failed to copy file link: ${err.message}`);
        }
    };

    useEffect(() => {
        fetchFolderData();
        fetchFiles();
    }, [search]);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error: {error}</p>;

    return (
        <div className="view-all-share-folder-files-request">
            {folderData && (
                <div className="folder-header">
                    <h2>{folderData.folder_name}</h2>
                    <p>{folderData.folder_description}</p>

                    <label>
                        <input
                            type="checkbox"
                            checked={folderData.sharable}
                            onChange={(e) => updateFolderShareStatus(e.target.checked)}
                        />
                        Folder Sharable
                    </label>

                    <button
                        onClick={copyFolderShareLink}
                        disabled={!folderData.sharable}
                        style={{ marginLeft: "10px" }}
                    >
                        Copy Folder Share Link
                    </button>
                </div>
            )}

            <button onClick={() => setShowPopup(true)} style={{ marginTop: "15px" }}>
                Upload File
            </button>

            {files.length === 0 ? (
                <p>No files found in this folder.</p>
            ) : (
                <ul>
                    {files.map((file) => (
                        <li key={file.file_serial}>
                            <strong>{file.file_name}</strong> - {file.file_description} ({file.file_type})
                            <br />

                            <label>
                                <input
                                    type="checkbox"
                                    checked={file.file_share_status}
                                    onChange={(e) =>
                                        updateFileShareStatus(file.file_serial, e.target.checked)
                                    }
                                />
                                File Sharable
                            </label>

                            <button
                                onClick={() => copyFileShareLink(file.file_serial)}
                                disabled={!file.file_share_status}
                                style={{ marginLeft: "10px" }}
                            >
                                Copy File Share Link
                            </button>
                        </li>
                    ))}
                </ul>
            )}

            {showPopup && (
                <UploadShareFilePopup
                    onClose={() => setShowPopup(false)}
                    onUploadSuccess={fetchFiles}
                    folderSerial={folderSerial}
                />
            )}
        </div>
    );
};

export default ViewAllShareFolderFilesRequest;
