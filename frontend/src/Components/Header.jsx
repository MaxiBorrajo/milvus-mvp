import React from "react";
import { Link } from "react-router-dom";

const Header = ({ title, showLogo = true }) => {
  return (
    <header className="app-header">
      {showLogo && (
        <div className="logo">
          <Link to="/" className="back-btn">
            <span role="img" aria-label="logo">
              🚀
            </span>
          </Link>
        </div>
      )}
      <h1>{title || "Milvus MVP"}</h1>
    </header>
  );
};

export default Header;
