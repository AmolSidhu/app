import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import MyUploadsRequest from "../../Components/Requests/MyUploadsRequest";

const MyVideoUploadsPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "My Video Uploads";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <h1>My Video Uploads</h1>
            <MyUploadsRequest />
        </div>
    );
}

export default MyVideoUploadsPage;