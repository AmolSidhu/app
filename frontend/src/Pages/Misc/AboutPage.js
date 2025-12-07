import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import ServerPatchDataRequest from "../../Components/Requests/ServerPatchDataRequest";

const AboutPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "About";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <ServerPatchDataRequest />
        </div>
    );
}

export default AboutPage;