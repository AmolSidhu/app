import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";

const SearchArticlesPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Articles Search";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Search Articles</h1>
        </div>
    );
}

export default SearchArticlesPage;