import React, {useEffect} from "react";
import MainNavbar from "../../Components/Static/MainNavbar";
import EditPictureForm from "../../Components/Forms/EditPictureForm";

const EditPicturePage = () => {
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
            <EditPictureForm />
        </div>
    );
}

export default EditPicturePage;