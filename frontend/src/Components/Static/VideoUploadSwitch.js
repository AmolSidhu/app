import React, { useState } from 'react';
import BatchVideoUploadForm from '../Forms/BatchVideoUploadForm';
import SingleVideoUploadForm from '../Forms/SingleVideoUploadForm';

const VideoUploadSwitch = () => {
    const [isBatchUpload, setIsBatchUpload] = useState(false);
// eslint-disable-next-line
    const handleToggle = () => {
        setIsBatchUpload(!isBatchUpload);
    };

    return (
        <div className="app-container">
            <div className="toggle-buttons">
                <button onClick={() => setIsBatchUpload(false)} className={!isBatchUpload ? 'active' : ''}>
                    Single Upload
                </button>
                <button onClick={() => setIsBatchUpload(true)} className={isBatchUpload ? 'active' : ''}>
                    Batch Upload
                </button>
            </div>
            <div className="form-container">
                {isBatchUpload ? <BatchVideoUploadForm /> : <SingleVideoUploadForm />}
            </div>
        </div>
    );
};

export default VideoUploadSwitch;
