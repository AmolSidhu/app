import React from "react";
import EditDataSourceForm from "../Forms/EditDataSourceForm";
import UploadDataSourceForm from "../Forms/UploadDataSourceForm";

const DataSourceSwitch = () => {
    const [isUpload, setIsUpload] = React.useState(false);
    // eslint-disable-next-line
    const handleToggle = () => {
        setIsUpload(!isUpload);
    };

    return (
        <div className="data-source-switch">
            <div className="toggle-buttons">
                <button onClick={() => setIsUpload(false)} className={!isUpload ? 'active' : ''}>
                    Edit Data Source
                </button>
                <button onClick={() => setIsUpload(true)} className={isUpload ? 'active' : ''}>
                    Upload Data Source
                </button>
            </div>
            <div className="form-container">
                {isUpload ? <UploadDataSourceForm /> : <EditDataSourceForm />}
            </div>
        </div>
    );
}

export default DataSourceSwitch;