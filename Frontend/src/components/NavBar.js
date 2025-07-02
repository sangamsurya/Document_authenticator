import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import "./NavBar.css";
import { HamburgetMenuClose, HamburgetMenuOpen } from "./Icons";

function NavBar() {
  const [click, setClick] = useState(false);

  const handleClick = () => setClick(!click);
  return (
    <>
      <nav className="navbar">
        <div className="nav-container">
          <NavLink exact to="/" className="nav-logo">
            <span>Document authenticator</span>
          </NavLink>
          <ul className={click ? "nav-menu active" : "nav-menu"}>
            <li className="nav-item">
              <NavLink
                exact
                to="/"
                activeClassName="active"
                className="nav-links"
                onClick={handleClick}
              >
                Home
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                exact
                to="/Sender"
                activeClassName="active"
                className="nav-links"
                onClick={handleClick}
              >
                Sender
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                exact
                to="/Receiver"
                activeClassName="active"
                className="nav-links"
                onClick={handleClick}
              >
                Receiver
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                exact
                to="/VoiceChecker"
                activeClassName="active"
                className="nav-links"
                onClick={handleClick}
              >
                Voice Checker
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                exact
                to="/ProjectContributor"
                activeClassName="active"
                className="nav-links"
                onClick={handleClick}
              >
                Project Contributor
              </NavLink>
            </li>
          </ul>
          <div className="nav-icon" onClick={handleClick}>
            {/* <i className={click ? "fas fa-times" : "fas fa-bars"}></i> */}

            {click ? (
              <span className="icon">
                <HamburgetMenuOpen />{" "}
              </span>
            ) : (
              <span className="icon">
                <HamburgetMenuClose />
              </span>
            )}
          </div>
        </div>
      </nav>
    </>
  );
}

export default NavBar;
