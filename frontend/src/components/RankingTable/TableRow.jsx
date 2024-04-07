// React hooks
import { useEffect, useRef } from "react";

// React router component
import { Link } from "react-router-dom";

// Chart component
import { createChart } from "lightweight-charts";


// Graph component
function TradingViewWidget(props) {
    const container = useRef();
    useEffect(() => {
        // Graph configuration
        const chart = createChart(container.current, {
            width: 300,
            height: 50,
            layout: {
                background: { type: "solid", color: "white" }
            },
            grid: {
                vertLines: { visible: false },
                horzLines: { visible: false },
            },
        });

        // Calculate the average value within the given dataset
        // and set it to be the baseline
        let avgValue = 0;
        Array.from(props.graphData).forEach((object) => {
            avgValue += object.value;
        })
        avgValue = avgValue / Array.from(props.graphData).length;

        // Set price precision
        let pricePrecision = 2;
        if (props.product === "SHIB-USD" || props.product === "DOGE-USD" || props.product === "TRX-USD") {
            pricePrecision = props.product === "SHIB-USD" ? 7 : 4;
        }
        const areaSeries = chart.addBaselineSeries({
            lineWidth: 2,
            baseValue: {
                type: "price",
                price: avgValue,
            },
            priceFormat: {
                precision: pricePrecision,
                minMove: 0.00000001,
            }
        });

        // Vertical axis options
        chart.priceScale("right").applyOptions({
            borderVisible: false,
            entireTextOnly: true,
        });

        // Horizontal axis options
        chart.timeScale().applyOptions({
            visible: false,
            fixLeftEdge: true,
            fixRightEdge: true,
            lockVisibleTimeRangeOnResize: true,
        })

        try {
            areaSeries.setData(Array.from(props.graphData));
        }
        catch {
            console.log(props.product);
        }
        
        return (() => {
            chart.remove();
        })
    }, [props.graphData]);

    return (
        <div className="minichart" ref={container}></div>
    );
}

// Represent the up/down carets that appear besides the numbers
function Caret(props) {
    if (parseFloat(props.value) > 0) {
        return (<span className="caret-up"></span>);
    }
    else if (parseFloat(props.value) < 0) {
        return (<span className="caret-down"></span>);
    }
    else {
        return (<></>);
    }
}

// Table Cell component
function TableCell(props) {
    return (
        <td className="">
            <Link to={`analysis/${props.product}`}>
                <div className={props.className}>
                    {props.requiresCaret ? <Caret value={props.value} /> : null}
                    {props.value}
                </div>
            </Link>
        </td>
    );
}

// Find appropriate CSS class based on the given numeric value
function getCssClass(value, paramType) {
    let cssClass = "";   
    if (value > 0) {
        // Special case, the higher the volatility, the riskier the product is
        if (paramType === "volatility") {
            if (value >= 0.5) {
                cssClass = (value >= 1) ? "down-extreme" : "down-medium";
            }
            else {
                cssClass = "down";
            }
        }
        else {
            if (value >= 0.5) {
                cssClass = (value >= 1) ? "up-extreme": "up-medium";
            }
            else {
                cssClass = "up";
            }
        }
    }
    if (value < 0) {
        if (value <= -0.5) {
            cssClass = (value <= -1) ? "down-extreme" : "down-medium";
        }
        else {
            cssClass = "down";
        }
    }

    return cssClass;
}

// Table Row component
function TableRow(props) {
    // Declare default parameters and obtain the rest from filter parameters
    const defaultParams = ["type", "product", "value", "absolute_change"];
    const periodParams = props.filterParams.periods.map((period) => {
        return period + "_relative_change";
    });
    const metricParams = props.filterParams.metrics;

    // The order of the parameters to be displayed will be the same as those in the following list
    const params = defaultParams.concat(periodParams).concat(metricParams);

    const pctClassParams = [
        "d_relative_change", "w_relative_change", "m_relative_change", 
        "y_relative_change", "volatility", "expected_return"
    ];

    const tableCellComps = []
    for (let i = 0; i < params.length; i++) {
        const isOfPctClass = pctClassParams.includes(params[i]) ? true : false;
        let value = props.object[params[i]];   
        if (typeof value === "number") {
            value = new Intl.NumberFormat(
                "en-US",
                { maximumSignificantDigits: 7 }
            ).format(value);
        }

        // Assign color to table cell 
        const cssClass = getCssClass(value, params[i]);

        // Add caret component if the parameter reflects the daily change in real value
        const requiresCaret = params[i] === "absolute_change" ? true : false;

        tableCellComps.push(
            <TableCell 
                key={`table-cell-${i}`}
                value={ isOfPctClass ? Math.trunc(value*100) : value }
                className={ 
                    isOfPctClass ? "percentage " + cssClass 
                    : ([3].includes(i)) ? "text-start" 
                    : ([2].includes(i)) ? "text-end"
                    : "" 
                }
                requiresCaret={requiresCaret}
                product={props.object.product}
                // symbol={props.object.symbol}
            />
        );
    }

    return (
        <tr key={props.id}>
            <th scope="row">
                {props.id}
            </th>
                {tableCellComps}
            <td>
                <TradingViewWidget
                    graphData={props.object.graphing_data}
                    product={props.object.symbol}
                />
            </td>
        </tr>
    );
}

export default TableRow;
