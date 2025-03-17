import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const MyYoutubeListsPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "My Youtube Lists";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>My Youtube Lists</h1>
        </div>
    );
}

export default MyYoutubeListsPage;