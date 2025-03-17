import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import DataSourceSwitch from "../../Components/Static/DataSourceSwitch";

const UploadDataSourcePage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Upload Data";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Upload Data Source</h1>
        <DataSourceSwitch />
        </div>
    );
}

export default UploadDataSourcePage;