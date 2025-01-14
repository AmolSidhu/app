import React, {useEffect} from "react";
import RegisterationForm from "../../Components/Forms/RegistrationForm";
import LoginNavbar from "../../Components/Static/LoginNavbar";

const RegisterationPage = () => {
    useEffect(() => {
        document.title = "Register";
    }, []);
    return (
        <div>
            <LoginNavbar />
            <h1>Register</h1>
            <RegisterationForm />
        </div>
    );
}

export default RegisterationPage;