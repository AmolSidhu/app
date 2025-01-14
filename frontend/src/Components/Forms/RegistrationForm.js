import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
import Form from 'react-bootstrap/Form';
import { useNavigate } from 'react-router-dom';
import server from '../Static/Constants';

const RegisterationForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [username, setUsername] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const RegisterUser = (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        fetch(`${server}/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password, confirmPassword }),
        })
        .then((res) => {
            if (!res.ok) {
                setError(`An error has occured during registration ${res.status}`);
                throw new Error('Network response error');
                
            }
            return res.json();
        })
        .then((data) => {
            if (data.msg) {
                navigate('/verification/');
            } else {
                console.log(data.msg);
                setError(`An error has occured during registration ${data.msg}`);
            }
        })
        .catch((error) => {
            if (error.response) {
            }
            setError(`An error has occured during registration ${error}`);
        });
};

return(
    <div className="standard_form_auth">
        <Form onSubmit={RegisterUser}>
            <Form.Group>
                <Form.Label>Username</Form.Label>
                <Form.Control
                    type="text"
                    placeholder="Enter username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
            </Form.Group>
            <Form.Group>
                <Form.Label>Email</Form.Label>
                <Form.Control
                    type="email"
                    placeholder="Enter email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
            </Form.Group>
            <Form.Group>
                <Form.Label>Password</Form.Label>
                <Form.Control
                    type="password"
                    placeholder="Enter password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
            </Form.Group>
            <Form.Group>
                <Form.Label>Confirm Password</Form.Label>
                <Form.Control
                    type="password"
                    placeholder="Confirm password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                />
            </Form.Group>
            <Button variant="primary" type="submit" className="btn btn-primary btn-block">
                Register
            </Button>
        </Form>
        <p>{error}</p>
    </div>
);
};
export default RegisterationForm;