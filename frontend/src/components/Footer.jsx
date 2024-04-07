function Footer() {
    return (
        <footer>
            <div className="container-fluid">
                <div className="d-flex flex-row">
                    <div className="p-2 logo">
                        <a href="">Market Statistics</a>
                    </div>
                    <div className="p-2">
                        <ul className="list-group">
                            <li className="list-group-item"><h5>Sitemap</h5></li>
                            <li className="list-group-item"><a href="">Home</a></li>
                            <li className="list-group-item"><a href="">Economic Calendar</a></li>
                            <li className="list-group-item"><a href="">Analysis</a></li>
                        </ul>
                    </div>
                    <div className="p-2">
                        <ul className="list-group">
                            <li className="list-group-item"><h5>About</h5></li>
                            <li className="list-group-item"><a href="">Our Team</a></li>
                            <li className="list-group-item"><a href="">Analysis Metrics</a></li>
                        </ul>
                    </div>
                </div>
                <hr />
                <p>
                    <b>Disclaimer : </b> 
                    Any information provided by this page is subjective to personal opinions and 
                    does not act as a real investment advice nor an investment strategy. Please consult
                    professionals before making any decisions with your capital.
                </p>
            </div>
        </footer>
    );
}

export default Footer;
