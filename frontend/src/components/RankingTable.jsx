import { useState, useMemo, useRef } from "react";

import ToolBar from "./RankingTable/ToolBar";
import TableHead from "./RankingTable/TableHead";
import TableBody from "./RankingTable/TableBody";
import Pagination from "./RankingTable/Pagination";


// Assign an ID to each element based on its position in a list
function assignId(dataList) {
    for (let i = 0; i < dataList.length; i++) {
        dataList[i].id = i + 1;
    }
}

// Compare two objects of JSON-style
function isEqual(a, b) {
    if (JSON.stringify(a) === JSON.stringify(b)) {
        return true;
    }
    return false;
}

// Get the appropriate URL based on asset class selection
function getURL(BASE_URL, selectedType) {
    const URL_SUFFIX = selectedType === "" ? "" : "assetclass=" + selectedType + "/";

    return BASE_URL + URL_SUFFIX;
}

// Handle all data request and retrieval -related functionalities
class DataRequest {
    constructor(defaultRequestData, setData) {
        this.defaultRequestData = defaultRequestData;
        this.setData = setData;
    }

    constructRequest(URL, requestData) {
        let request = null;

        // Make a GET request on page load/reload or when 
        // there's no changes in the payload
        if (isEqual(this.defaultRequestData, requestData)) {
            request = new Request(URL);
        }
        // Make a POST request when there's changes in the payload,
        // typically due to users' form submission
        else {
            request = new Request(URL, {
                method: "POST",
                headers: {
                    "Content-type": "application/json; charset=UTF-8",
                },
                body: JSON.stringify(requestData),
            });
        }

        return request;
    }

    retrieveData(URL, requestData) {
        const request = this.constructRequest(URL, requestData);

        fetch(request)
        .then((response) => response.json())
        .then((jsonData) => {
            assignId(jsonData);
            this.setData(jsonData);
        })
        .catch((error) => console.log(error));
    }
}

// Handle all sorting-related functionalities
class DataSorting {
    constructor(sortConfig, setSortConfig) {
        this.sortConfig = sortConfig;
        this.setSortConfig = setSortConfig;
    }

    sortByConfig(key, direction) {
        return function(a, b) {
            if (a[key] < b[key]) {
                return direction ? -1 : 1;
            }
            else if (a[key] > b[key]) {
                return direction ? 1 : -1;
            }
            else {
                return 0;
            }
        }
    }

    requestSort(key) {
        let ascending = true;
        if (this.sortConfig.key === key && this.sortConfig.ascending === true) {
            ascending = false;
        }
        this.setSortConfig({ key, ascending }); 
    }

    sort(data) {
        const sortingFunc = this.sortByConfig(this.sortConfig.key, this.sortConfig.ascending);
        data.sort(sortingFunc);   
        assignId(data);
    }
}

// Handle all pagination-related functionalities
class Paginator {
    constructor(currentPage, setCurrentPage, 
                numOfRows, setNumOfRows) {
        this.currentPage = currentPage;
        this.setCurrentPage = setCurrentPage;
        this.numOfRows = numOfRows;
        this.setNumOfRows = setNumOfRows;
    }

    resetPagination = () => {
        this.setCurrentPage(1);
    }

    setTotalNumOfPages = (num) => {
        this.totalNumOfPages = num;
    }

    decrementPage = () => {
        if (this.currentPage > 1) {
            this.setCurrentPage(this.currentPage - 1);
        }
    }

    incrementPage = () => {
        if (this.currentPage < this.totalNumOfPages) {
            this.setCurrentPage(this.currentPage + 1);
        }
    }

    sliceData = (data) => {
        const start = Number(this.currentPage - 1) * Number(this.numOfRows);
        const end = Number(start) + Number(this.numOfRows);

        return data.slice(start, end);
    }
}


// Main component
function RankingTable(props) {
    // ----- Section: Filter data by asset class -----
    const [dataByAssetClass, setDataByAssetClass] = useState("");
    // ----- End section -----


    // ----- Section: Filter data range and add/remove metrics -----
    const today = new Date().toISOString().substring(0, 10);
    const defaultFilterParams = {
        "metrics": ["expected_return", "volatility", "updown_ratio"],
        "periods": ["d", "w", "m", "y"], 
        "date_range": { from: "2024-01-01", to: today } 
    };
    const [filterParams, setFilterParams] = useState(defaultFilterParams);
    // ----- End section -----

    
    // ----- Section: Request and retrieve data -----
    const [data, setData] = useState([]);
    const dataRequest = new DataRequest(defaultFilterParams, setData);

    // Retrieve data records with full-fledged information
    useMemo(() => {
        const BASE_URL = "http://localhost:8000/";
        const URL = getURL(BASE_URL, dataByAssetClass);

        dataRequest.retrieveData(URL, filterParams);
    }, [dataByAssetClass, filterParams]);
    // ----- End section -----


    // ----- Section: Pagination handle -----
    const [currentPage, setCurrentPage] = useState(1);
    const [numOfRows, setNumOfRows] = useState(10);
    const paginator = new Paginator(currentPage, setCurrentPage, 
                                    numOfRows, setNumOfRows);
    // ----- End section -----


    // ----- Section: Sorting data -----
    // Sorting parameter
    const [sortConfig, setSortConfig] = useState({
        key: "y_relative_change",
        ascending: false,
    });
    const dataSorting = new DataSorting(sortConfig, setSortConfig);

    useMemo(() => {
        dataSorting.sort(data);
        setData(data);
        paginator.resetPagination();
    }, [data, sortConfig]);
    // ----- End section -----

    return (
        <>
            <h4>Market Update: YTD - {`${ today }`}</h4>
            <div className="container-fluid ranking-table rounded-3">
                <div className="row">
                    <div className="container">
                        <ToolBar
                            dataByAssetClass={dataByAssetClass}
                            setDataByAssetClass={setDataByAssetClass}
                            paginator={paginator}
                            setFilterParams={setFilterParams}
                        />
                        <table className="table table-hover">
                            <TableHead 
                                dataSorting={dataSorting}
                                filterParams={filterParams}
                            />
                            <TableBody
                                data={paginator.sliceData(data)}
                                filterParams={filterParams}
                            />
                        </table>
                        <Pagination
                            dataLength={data.length}
                            paginator={paginator}
                        />
                    </div>
                </div>
            </div>
        </>
    );
}

export default RankingTable;
