import { useState, useEffect } from "react";


function ColumnHeader(props) {
    return (
        <th 
            scope="col"
            key={props.id}
            className={props.className}
        >
            <button
                onClick={() => props.dataSorting.requestSort(props.object.name)}
            >
                {props.object.alias}
            </button>
        </th>
    );
}

function TableHead(props) {
    // Default headers lists
    const defaultHeaders = [
        { id: "id", name: "id", alias: "#" },
        { id: "type", name: "type", alias: "Type" },
        { id: "product", name: "product", alias: "Product" },
        { id: "value", name: "value", alias: "Last Value" },
        { id: "absolute_change", name: "absolute_change", alias: "24h Change" },
    ];
    const customizableHeaders = [
        { id: "d", name: "d_relative_change", alias: "Avg. %D" },
        { id: "w", name: "w_relative_change", alias: "Avg. %W" },
        { id: "m", name: "m_relative_change", alias: "Avg. %M" },
        { id: "y", name: "y_relative_change", alias: "%Y" },
        { id: "updown_ratio", name: "updown_ratio", alias: "Up/Down Ratio" },
        { id: "volatility", name: "volatility", alias: "Ann. Volatility" },
        { id: "expected_return", name: "expected_return", alias: "Ann. Exp. Return" },
        // { id: "beta_measure", name: "beta_measure", alias: "Beta" },
        // { id: "nearest_extremes", name: "nearest_extremes", alias: "% from Nearest High/Low" },
    ];
    const defaultLastColumn = [
        { id: "minichart", name: "graph", alias: "Last Values (Max. 30 Days)" }
    ];
    
    // Record the headers to be displayed by user' selection
    const [headers, setHeaders] = useState(defaultHeaders
                                            .concat(customizableHeaders)
                                            .concat(defaultLastColumn));
    
    // Separately update headers when there's change in filter parameters
    useEffect(() => {
        const metrics = props.filterParams.metrics.map((metric) => {
            return customizableHeaders.filter((header) => {
                if (header.id === metric) {
                    return header
                }
            }).filter(n => n)[0];
        });
        
        const periods = props.filterParams.periods.map((period) => {
            return customizableHeaders.filter((header) => {
                if (header.id === period) {
                    return header
                }
            }).filter(n => n)[0];
        });

        setHeaders(defaultHeaders
                    .concat(periods)
                    .concat(metrics)
                    .concat(defaultLastColumn));
    }, [props.filterParams]);

    const headerComps = headers.map((object, index) => 
        <ColumnHeader 
            key={object.id}
            object={object}
            dataSorting={props.dataSorting}
            className={
                ([4].includes(index)) ? "text-start" 
                : ([3].includes(index)) ? "text-end"
                : ""
            }
        />
    );

    return (
        <thead>
            <tr>
                {headerComps}
            </tr>
        </thead>
    );
}

export default TableHead;
