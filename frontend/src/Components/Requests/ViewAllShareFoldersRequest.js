import React, { useEffect, useState } from "react";
import server from "../Static/Constants";
import CreateFileShareFolderPopup from "../Popups/CreateFileShareFolderPopup";

const ViewAllShareFoldersRequest = () => {
    const [folders, setFolders] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showPopup, setShowPopup] = useState(false);

    const fetchFolders = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${server}/get/folders`, {
                method: "GET",
                headers: {
                    "Authorization": localStorage.getItem("token") || "",
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || "Error fetching folders");
            }
            setFolders(data.data || {});
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFolders();
    }, []);

    if (loading) return <p>Loading folders...</p>;
    if (error) return <p>Error: {error}</p>;

    return (
        <div className="view-all-share-files-request">
            <h2>View All Shared Folders</h2>

            <button onClick={() => setShowPopup(true)}>
                + Create New Folder
            </button>

            {showPopup && (
                <CreateFileShareFolderPopup
                    onClose={() => setShowPopup(false)}
                    onCreateSuccess={fetchFolders}
                />
            )}

            {Object.keys(folders).length === 0 ? (
                <p>No folders found</p>
            ) : (
                <ul>
                    {Object.entries(folders).map(([serial, folder]) => (
                        <li key={serial}>
                            <strong>{folder.folder_name}</strong> - {folder.folder_description}
                            {" "}
                            <a href={`/files/viewfolder/?serial=${serial}`}>
                                View Folder
                            </a>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default ViewAllShareFoldersRequest;
