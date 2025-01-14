import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const HomePage = () => {
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
        <h1>Home</h1>
        </div>
    );
}

export default HomePage;