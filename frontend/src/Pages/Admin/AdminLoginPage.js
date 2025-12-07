import React, {useEffect} from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import AdminNavbar from '../../Components/Static/AdminNavbar';
import AdminLoginForm from '../../Components/Forms/AdminLoginForm';

const AdminLoginPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "Admin Login";
        }
    }, []);

    return (
        <>
            <MainNavbar />
            <AdminNavbar />
            <div>
                <h1>Admin Login Page</h1>  
            </div>
            <AdminLoginForm />
        </>
    );
};

export default AdminLoginPage;