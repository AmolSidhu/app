import React, {useEffect} from "react";
import VideoUploadSwitch from "../../Components/Static/VideoUploadSwitch";
import MainNavbar from "../../Components/Static/MainNavbar";

const VideoUploadPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Uploads";
        }
    }, []);
    return (
        <div>
            <MainNavbar />
            <h1>Upload Page</h1>
            <VideoUploadSwitch />
        </div>
    );
}

export default VideoUploadPage;