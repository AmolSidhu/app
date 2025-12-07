import React, {useEffect} from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import AdminNavbar from '../../Components/Static/AdminNavbar';

const AdminDataPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "Admin Data Page";
        }
    }, []);

    useEffect(() => {
        const adminToken = localStorage.getItem("adminToken");
        if (!adminToken) {
            window.location.href = "/admin/login/";
        }
    }, []);

    return (
        <>
            <MainNavbar />
            <AdminNavbar />
            <div>
                <h1>Admin Data Page</h1>
            </div>
        </>
    );
};

export default AdminDataPage;