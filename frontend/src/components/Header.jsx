import { useState } from "react";
import { Link } from "react-router-dom";


function Header() {
    const [display, setDisplay] = useState("none")

    function showMenu() {
        if (display === "block") {
            setDisplay("none");
        }
        else {
            setDisplay("block");
        }
    }

    return (
        <header>
            <div className="logo">
                <a href="">Market Statistics</a>
            </div>
            <nav className="d-flex flex-row justify-content-between align-items-center">
                <Link
                    to={""}
                    className="me-auto"
                >
                    <div className="p-2 px-3">Home</div>
                </Link>
                {/* <div className="p-2 px-3 me-auto"><a href="">Analysis</a></div> */}
                <div className="p-2">
                    <form action="" className="d-flex">
                        <input className="form-control me-2" type="search" placeholder="Search" aria-label="Search" />
                        <button className="btn btn-outline-success" type="submit">Search</button>
                    </form>
                </div>
                <div className="p-2 px-3">
                    <div className="dropdown me-2">
                        <button 
                            className="btn btn-primary dropdown-toggle"
                            onMouseOver={showMenu}>
                            Login
                        </button>
                        <ul
                            className="dropdown-menu"
                            style={{display: display}}
                            onMouseLeave={showMenu}
                        >
                            <li><a className="dropdown-item" href="#">Login</a></li>
                            <li><a className="dropdown-item" href="#">Register</a></li>
                            <li><a className="dropdown-item" href="#">Account</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
        </header>
    );
}

export default Header;
