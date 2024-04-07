function PageItem(props) {
    return (
        <li 
            className="page-item"
            key={props.id}
        >
            <a  
                className={`page-link ${props.currentPage === props.pageNumber ? "active" : ""}`} 
                onClick={() => props.navigatePage(props.pageNumber)}
                href="#"
            >
                {props.pageNumber}
            </a>
        </li>
    );
}

function Pagination(props) {
    // Calculate the total number of page items to show
    const rowPerPage = props.paginator.numOfRows;
    const dataLength = props.dataLength;
    const totalNumOfPages = Math.ceil(dataLength / rowPerPage);
    props.paginator.setTotalNumOfPages(totalNumOfPages);

    // Create a list of pagination item components with corresponding properties
    const pageItemCompsList = []
    for (let i = 1; i <= totalNumOfPages; i++) {
        pageItemCompsList.push(
            <PageItem 
                key={`page-item-${i}`}
                pageNumber={i}
                currentPage={props.paginator.currentPage}
                navigatePage={props.paginator.setCurrentPage}
            />
        );
    }

    return (
        <nav aria-label="...">
            <ul className="pagination">
                <li className="page-item">
                    <a 
                        id="pagination-decrement"
                        className="page-link"
                        onClick={props.paginator.decrementPage}
                        href="#"
                    >
                        Previous
                    </a>
                </li>
                {pageItemCompsList}
                <li className="page-item">
                    <a 
                        id="pagination-increment"
                        className="page-link"
                        onClick={props.paginator.incrementPage}
                        href="#"
                    >
                        Next
                    </a>
                </li>
            </ul>
        </nav>
    );
}

export default Pagination;
