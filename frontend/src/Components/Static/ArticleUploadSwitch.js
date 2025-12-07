import React from "react";
import ArticleFileUploadForm from "../Forms/ArticleFileUploadForm";
import ArticleUploadForm from "../Forms/ArticleUploadForm";

const ArticleUploadSwitch = () => {
    const [isUpload, setIsUpload] = React.useState(false);
    // eslint-disable-next-line
    const handleToggle = () => {
        setIsUpload(!isUpload);
    };

    return (
        <div className="data-source-switch">
            <div className="toggle-buttons">
                <button onClick={() => setIsUpload(false)} className={!isUpload ? 'active' : ''}>
                    Upload Article
                </button>
                <button onClick={() => setIsUpload(true)} className={isUpload ? 'active' : ''}>
                    Upload Article File
                </button>
            </div>
            <div className="form-container">
                {isUpload ? <ArticleFileUploadForm /> : <ArticleUploadForm />}
            </div>
        </div>
    );
}

export default ArticleUploadSwitch;