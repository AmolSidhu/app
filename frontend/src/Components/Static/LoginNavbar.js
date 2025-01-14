import React from "react";
import { Container,Navbar, Nav } from "react-bootstrap";

const LoginNavbar = () => {
    return(
        <Navbar className="navbar">
            <Container className="container">
                <Nav.Link className="nav-link" href="/login">Login</Nav.Link>
                <Nav.Link className="nav-link" href="/verification">Verify</Nav.Link>
                <Nav.Link className="nav-link" href="/register">Register</Nav.Link>
            </Container>
        </Navbar>
    )
}

export default LoginNavbar;
