import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const YoutubeStreamPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Watch My Youtube";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Youtube Stream Page</h1>
        </div>
    );
}

export default YoutubeStreamPage;