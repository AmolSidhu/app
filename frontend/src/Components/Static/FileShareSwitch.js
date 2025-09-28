import React from "react";
import ViewAllShareFoldersRequest from "../Requests/ViewAllShareFoldersRequest";
import ViewAllShareFilesRequest from "../Requests/ViewAllShareFilesRequest";

const FileShareSwitch = () => {
    const [isUpload, setIsUpload] = React.useState(false);
    // eslint-disable-next-line
    const handleToggle = () => {
        setIsUpload(!isUpload);
    };

    return (
        <div className="data-source-switch">
            <div className="toggle-buttons">
                <button onClick={() => setIsUpload(false)} className={!isUpload ? 'active' : ''}>
                    View Shared Files
                </button>
                <button onClick={() => setIsUpload(true)} className={isUpload ? 'active' : ''}>
                    View Shared Folders
                </button>
            </div>
            <div className="form-container">
                {isUpload ? <ViewAllShareFoldersRequest /> : <ViewAllShareFilesRequest />}
            </div>
        </div>
    );
}

export default FileShareSwitch;