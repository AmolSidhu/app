import React, {useState} from 'react';
import { useNavigate } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import server from '../Static/Constants';

const AdminLoginForm = () => {
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const LoginAdmin = (e) => {
        e.preventDefault();

        fetch(`${server}/admins/login/`, {
            method: "PATCH",
            headers: {
                Authorization: localStorage.getItem("token"),
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email }),
        })
        .then((res) => {
            if (!res.ok) {
                setError(`An error occurred during admin login (${res.status})`);
                throw new Error("Network response error");
            }
            return res.json();
        })
        .then((data) => {
            localStorage.setItem("adminToken", data.admin_token);
            navigate("/admin/data/");
        })
        .catch((error) => {
            console.error("Error during admin login:", error);
        });
    };

    return (
        <Form onSubmit={LoginAdmin}>
            <Form.Group controlId="formBasicEmail">
                <Form.Label>Email address</Form.Label>
                <Form.Control
                    type="email"
                    placeholder="Enter email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
            </Form.Group>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <Button variant="primary" type="submit">
                Login
            </Button>
        </Form>
    );
};

export default AdminLoginForm;