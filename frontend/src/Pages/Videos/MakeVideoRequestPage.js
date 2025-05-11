import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import CreateVideoRequestForm from "../../Components/Forms/CreateVideoRequestForm";
const MakeVideoRequestPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Video Request";
        }
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Make A Video Request</h1>
        <CreateVideoRequestForm />
        </div>
    );
}

export default MakeVideoRequestPage;