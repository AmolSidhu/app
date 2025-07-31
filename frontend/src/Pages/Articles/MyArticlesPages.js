import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const MyArticlesPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "My Articles";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>My Articles</h1>
        </div>
    );
}

export default MyArticlesPage;