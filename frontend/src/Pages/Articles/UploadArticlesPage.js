import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const UploadArticlesPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Upload Articles";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Upload Articles</h1>
        </div>
    );
}

export default UploadArticlesPage;