import React, {useEffect} from "react";
import ScraperUploadForm from "../../Components/Forms/ScraperUploadForm";
import MainNavbar from "../../Components/Static/MainNavbar";

const UploadScraperPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Upload Scraper";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Upload Scraper</h1>
        <ScraperUploadForm />
        </div>
    );
}

export default UploadScraperPage;