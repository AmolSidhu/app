import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import server from "../Static/Constants";

const LoginForm = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const LoginUser = (e) => {
    e.preventDefault();

    console.log(email, password);
    fetch(`${server}/login/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    })
      .then((res) => {
        if (!res.ok) {
          setError(`An error occurred during login (${res.status})`);
          throw new Error("Network response error");
        }
        return res.json();
      })
      .then((data) => {
        if (data.token) {
          localStorage.setItem("token", data.token);
          navigate("/");
        } else {
          setError(`An error occurred during login (${data.msg})`);
        }
      })
      .catch((error) => {
        setError(`An error occurred during login (${error})`);
      });
  };

  return (
    <div className="standard_form_auth">
      <Form onSubmit={LoginUser}>
        <div>
          <Form.Group>
            <Form.Label>Email Address</Form.Label>
            <Form.Control
              type="email"
              value={email}
              placeholder="Enter email"
              onChange={(e) => setEmail(e.target.value)}
            />
          </Form.Group>
          <Form.Group>
            <Form.Label>Password</Form.Label>
            <Form.Control
              type="password"
              value={password}
              placeholder="Enter password"
              onChange={(e) => setPassword(e.target.value)}
            />
          </Form.Group>
        </div>
        <Form.Group>
          <Form.Check type="checkbox" label="Remember Me" />
        </Form.Group>
        <Button variant="primary" type="submit" className="btn btn-primary btn-block">
          Login
        </Button>
      </Form>
      <p>
        Forgot your password? <a href="/u/forgot-password/">Reset Password</a>
      </p>
      <p>{error}</p>
    </div>
  );
};

export default LoginForm;
