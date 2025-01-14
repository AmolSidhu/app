import React, {useEffect} from "react";
import VerificationForm from "../../Components/Forms/VerificationForm";
import LoginNavbar from "../../Components/Static/LoginNavbar";

const VerificationPage = () => {
    useEffect(() => {
        document.title = "Verification";
    }, []);
    return (
        <div>
            <LoginNavbar />
            <h1>Verification</h1>
            <VerificationForm />
        </div>
    );
}

export default VerificationPage;