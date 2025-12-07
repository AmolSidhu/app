import React, {useEffect} from "react";
import LoginNavbar from "../../Components/Static/LoginNavbar";
import ForgotPasswordForm from "../../Components/Forms/ForgotPasswordForm";

const ForgotPasswordPage = () => {
    useEffect(() => {
        document.title = "Forgot Password";
    }, []);
    return (
        <div>
            <LoginNavbar />
            <ForgotPasswordForm />
        </div>
    );
};

export default ForgotPasswordPage;