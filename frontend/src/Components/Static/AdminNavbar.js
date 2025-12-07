import React, { useState } from "react";
import { Container, Nav, Navbar, NavDropdown, Button } from "react-bootstrap";

const AdminNavbar = () => {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <Navbar
        expand="lg"
        expanded={expanded}
        bg="light"
        variant="light"
        className="main-navbar shadow-sm"
      >
        <Container fluid className="px-4">
          <Navbar.Brand href="/admin/data/">Admin Home</Navbar.Brand>

          <Navbar.Toggle
            aria-controls="basic-navbar-nav"
            onClick={() => setExpanded((v) => !v)}
          />

          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="flex-grow-1 justify-content-start flex-wrap align-items-center">
              <NavDropdown title="Approvals" id="pictures-dropdown" className="me-3">
                <NavDropdown.Item href="/admin/videorequests/">Video Approvals</NavDropdown.Item>
              </NavDropdown>
            </Nav>
            
            </Navbar.Collapse>
        </Container>
      </Navbar>
    </>
  );
};

export default AdminNavbar;