import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import VideoTitleSearchResultsRequest from "../../Components/Requests/VideoTitleSearchResultsRequest";

const VideoTitleSearchPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Home";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <VideoTitleSearchResultsRequest />
        </div>
    );
}

export default VideoTitleSearchPage;