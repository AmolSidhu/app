import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import MusicAlbumsRequest from "../../Components/Requests/MusicAlbumsRequest";

const ViewAllMusicAlbumsPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "View All Music Albums";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>View All Music Albums Page</h1>
        <MusicAlbumsRequest />
        </div>
    );
}

export default ViewAllMusicAlbumsPage;