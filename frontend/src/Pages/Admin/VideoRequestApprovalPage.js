import React, { useEffect } from 'react';
import MainNavbar from '../../Components/Static/MainNavbar';
import AdminNavbar from '../../Components/Static/AdminNavbar';
import AdminVideoRequestApprovalRequest from '../../Components/Requests/AdminVideoRequestApprovalRequest';

const VideoRequestApprovalPage = () => {
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/login/";
        } else {
            document.title = "Admin Login";
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
                <h1>Video Request Approval Page</h1>  
            </div>
            <AdminVideoRequestApprovalRequest />
        </>
    );
};

export default VideoRequestApprovalPage;