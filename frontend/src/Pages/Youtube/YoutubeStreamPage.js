import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import YoutubeVideoStreamRequest from "../../Components/Requests/YoutubeVideoStreamRequest";
import YoutubeStreamInfoRequest from "../../Components/Requests/YoutubeStreamInfoRequest";

const YoutubeStreamPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Watch Video";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Youtube Stream Page</h1>
        <YoutubeVideoStreamRequest />
        <YoutubeStreamInfoRequest />
        </div>
    );
}

export default YoutubeStreamPage;