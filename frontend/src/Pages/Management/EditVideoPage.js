import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import EditVideoForm from "../../Components/Forms/EditVideoForm";

const EditVideoPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          window.location.href = "/login/";
        } else {
          document.title = "Edit Video";
        }
    }, []);

    return (
        <div>
            <MainNavbar />
            <h1>Edit Video</h1>
            <EditVideoForm />
        </div>
    );
}

export default EditVideoPage;