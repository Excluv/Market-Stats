import { useState } from "react";

import FilterForm from "./FilterForm";


// Drop-down list of no. data rows to show, represented as a component
function NumOfRowsSelect(props) {
    return (
        <select 
            id="" 
            onChange={(event) => {
                props.paginator.setNumOfRows(event.target.value);
                props.paginator.resetPagination();
            }}
        >
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
        </select>
    );
}

// Buttons representing the asset class filter
function ToolBarButton(props) {
    return (
        <button 
            key={props.id}
            className={`btn btn-light ${props.dataByAssetClass === props.object.assetClass ? "active" : ""}`}
            onClick={() => props.setDataByAssetClass(props.object.assetClass)}
        >
            {props.object.alias}
        </button>
    );
}

// Util. function: Show/hide HTML element
function displayHandle(displayState, setDisplayState) {
    return function () {
        if (displayState === "none") {
            setDisplayState("block");
        }
        else {
            setDisplayState("none");
        }
    }
}

function ToolBar(props) {
    // Default list of all available asset classes
    const UrlsList = [
        { id: "tb-btn-1", assetClass:"", alias: "All" },
        // { id: "tb-btn-2", assetClass:"Bond", alias: "Bond" },
        { id: "tb-btn-3", assetClass:"Commodity", alias: "Commodity" },
        { id: "tb-btn-4", assetClass:"Cryptocurrency", alias: "Cryptocurrency" },
        { id: "tb-btn-5", assetClass:"Forex", alias: "Forex" },
        { id: "tb-btn-6", assetClass:"Stock Index", alias: "Stock Index" },
        { id: "tb-btn-7", assetClass:"US Stock", alias: "US Stock" },
        // { id: "tb-btn-8", assetClass:"VN Stock", alias: "VN Stock" },
    ]

    // Convert the list into components
    const toolBarButtonCompList = UrlsList.map((object) => 
        <ToolBarButton
            key={object.id}
            dataByAssetClass={props.dataByAssetClass}
            object={object}
            setDataByAssetClass={props.setDataByAssetClass}
        />
    );

    // Toggle Filter Form component's display
    const [filterDisplayState, setFilterDisplayState] = useState("none");
    const showFilterForm = displayHandle(filterDisplayState, setFilterDisplayState);

    return (
        <div className="d-flex flex-row align-items-center toolbar">
            <div className="p-2">Asset Class |</div>
            <div className="p-2">
                {toolBarButtonCompList}
            </div>
            <div className="p-2 me-auto"></div>
            <div className="p-2">Show rows</div>
            <div className="p-2">
                <NumOfRowsSelect 
                    paginator={props.paginator}
                />
            </div>
            <div className="p-2 filter">
                <button 
                    className="btn btn-light dropdown-toggle"
                    onClick={showFilterForm}>
                    Filter
                </button>
                <div 
                    className="filter-box rounded-3"
                    style={{display: filterDisplayState}}
                >
                    <div className="box-head rounded-top-3">
                        <div className="title">Filter</div>
                    </div>
                    <div className="box-body">
                        <FilterForm 
                            setDisplay={setFilterDisplayState}
                            setFilterParams={props.setFilterParams}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ToolBar;
