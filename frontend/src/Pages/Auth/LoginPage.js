import React, {useEffect} from "react";
import LoginForm from "../../Components/Forms/LoginForm";
import LoginNavbar from "../../Components/Static/LoginNavbar";

const LoginPage = () => {
    useEffect(() => {
        document.title = "Login";
    }, []);
    return (
        <div>
            <LoginNavbar />
            <h1>Login</h1>
            <LoginForm />
        </div>
    );
}

export default LoginPage;