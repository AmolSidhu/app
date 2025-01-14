import React, { useState } from "react";
import { Container, Nav, Navbar, NavDropdown } from "react-bootstrap";
import LogoutRequest from "../Requests/LogoutRequest";

const MainNavbar = () => {
  const [expanded, setExpanded] = useState(false);

  const Logout = ({ onLogout }) => {
    return <button onClick={onLogout}>Logout</button>;
  };

  return (
    <Navbar
      expand="lg"
      expanded={expanded}
      className="main-navbar"
    >
      <Container>
        <Navbar.Brand href="/">Home</Navbar.Brand>
        <Navbar.Toggle
          aria-controls="basic-navbar-nav"
          onClick={() => setExpanded(!expanded)}
        />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="w-100 justify-content-between">
            <NavDropdown title="Pictures" id="pictures-dropdown" menuVariant="light">
              <NavDropdown.Item href="/albums/">Albums</NavDropdown.Item>
              <NavDropdown.Item href="/myalbums/">My Albums</NavDropdown.Item>
              <NavDropdown.Item href="/myfavourites/">My Favourites</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="Videos" id="video-dropdown" menuVariant="light">
              <NavDropdown.Item href="/video/list/">Videos</NavDropdown.Item>
              <NavDropdown.Item href="/video/upload/">Upload</NavDropdown.Item>
              <NavDropdown.Item href="/favourites/">Favourites</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="Profile" id="profile-dropdown" menuVariant="light">
              <NavDropdown.Item href="/albums/">Test 1</NavDropdown.Item>
              <NavDropdown.Item href="/myalbums/">Test 2</NavDropdown.Item>
              <NavDropdown.Item href="/myfavourites/">Test 3</NavDropdown.Item>
            </NavDropdown>

            <Logout onLogout={LogoutRequest} />
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default MainNavbar;
