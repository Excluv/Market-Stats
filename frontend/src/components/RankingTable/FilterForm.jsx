import { useState } from "react";


// Validate the user-input date range and set error message accordingly
function validateDateRange(startDate, endDate) {
    startDate = new Date(startDate);
    endDate = new Date(endDate);
    if (startDate >= endDate) {
        return false;
    }

    return true;
}

// Handle the changes in check boxes or date inputs
class FilterElementController {
    constructor(filterElements, setFilterElements, 
                errMessage=null, setErrMessage=null) {
        this.filterElements = filterElements;
        this.setFilterElements = setFilterElements;
        this.errMessage = errMessage;
        this.setErrMessage = setErrMessage;
    }

    resetErrMessage = () => {
        this.setErrMessage("");
    }

    changeCheckBoxState = (elementPosInList) => {
        const updatedElements = this.filterElements.map((object) => {
            // Find the correct check box, whose checking state is modified
            if (this.filterElements.indexOf(object) === elementPosInList) {
                object.checked = !(object.checked);
            }

            return object;
        });
        this.setFilterElements(updatedElements);
    }

    changeDateInput  = (dateType, newDateInput) => {
        this.resetErrMessage();

        if (dateType === "Start") {
            this.filterElements[0].date = newDateInput;
        }
        if (dateType === "End") {
            this.filterElements[1].date = newDateInput;
        }
        if (!validateDateRange(this.filterElements[0].date,  this.filterElements[1].date)) {
            this.setErrMessage("Error: End date must be greater than start date");
        }
        this.setFilterElements(this.filterElements);
    }
}

// ----- Section: Components -----
function FilterMetric(props) {
    return (
        <div className="metric">
            <input 
                type="checkbox"
                id={props.object.id} 
                checked={props.object.checked}
                onChange={() => props.onStateChange(props.index)}
            />
            <label htmlFor={props.object.id}>
                {props.object.name}
            </label>
        </div>
    );
}

function FilterDate(props) {
    return (
        <div key={props.id} className="metric date-range">
            <label htmlFor={props.object.id}>
                {props.object.name}
            </label>
            <input 
                id={props.object.id} 
                type="date" 
                className={"rounded-3"}
                onChange={(event) => props.onDateChange(props.object.name, event.target.value)}
            />
        </div>
    );
}

function FilterFormRow(props) {
    let compsList = [];
    const elementsList = props.elementsController.filterElements;

    if (props.title === "Metrics" || props.title === "Periods") {
        compsList = elementsList.map((object) => 
            <FilterMetric 
                key={object.id}
                index={elementsList.indexOf(object)}
                object={object}
                onStateChange={props.elementsController.changeCheckBoxState}
            />
        );
    }
    if (props.title === "Range") {
        compsList = elementsList.map((object) => 
            <FilterDate
                key={object.id}
                object={object}
                onDateChange={props.elementsController.changeDateInput}
            />
        );
    }

    return (
        <div className="d-flex flex-wrap align-items-center filter-form-row">
            <div className="title">{props.title}</div>
            <div className="content">
                {compsList}
            </div>
        </div>
    );
}
// ----- End section -----


// Filter Form component
function FilterForm(props) {
    // Filter elements
    const metricsList = [
        { id: "expected_return", name: "Expected Return", checked: true },
        { id: "volatility", name: "Volatility", checked: true },
        { id: "updown_ratio", name: "Up/Down Ratio", checked: true },
        // { id: "beta_measure", name: "Beta Measure", checked: true },
        // { id: "nearest_extremes", name: "Nearest Extremes", checked: false },
    ];
    const periodsList = [
        { id: "d", name: "D", checked: true },
        { id: "w", name: "W", checked: true },
        { id: "m", name: "M", checked: true },
        { id: "y", name: "Y", checked: true },
    ];
    const datesList = [
        { id: "start_date", name: "Start", date: "2024-01-01" },
        { id: "end_date", name: "End", date: new Date().toISOString().substring(0, 10) },
    ];

    // Record the states of filter elements
    const [metrics, setMetrics] = useState(metricsList);
    const [periods, setPeriods] = useState(periodsList);
    const [dateRange, setDateRange] = useState(datesList);

    // Error message
    const [errMessage, setErrMessage] = useState("");

    // Replace submit event
    function handleSubmit(event) {
        event.preventDefault();

        props.setFilterParams({
            "metrics": metrics.map((object) => {
                if (object.checked === true) {
                    return object.id;
                }
            }).filter(n => n),
            "periods": periods.map((object) => {
                if (object.checked === true) {
                    return object.id;
                }
            }).filter(n => n),
            "date_range": {
                from: dateRange[0].date,
                to: dateRange[1].date,
            }
        });
        props.setDisplay("none");
    }

    // Reset all form fields to default values
    function resetFilterFormFields(event) {
        event.preventDefault();
        setMetrics(metricsList);
        setPeriods(periodsList);
        setDateRange(datesList);
        setErrMessage("");
    }

    // Discard changes made to the form fields
    function cancelChanges(event) {
        event.preventDefault();
        resetFilterFormFields(event);
        props.setDisplay("none");
    }

    const metricsController = new FilterElementController(metrics, setMetrics);
    const periodsController = new FilterElementController(periods, setPeriods);
    const datesController = new FilterElementController(dateRange, setDateRange,
                                                        errMessage, setErrMessage);
    
    return (
        <form>
            <FilterFormRow
                title="Metrics"
                elementsController={metricsController}
            />
            <FilterFormRow 
                title="Periods"
                elementsController={periodsController}
            />
            <FilterFormRow 
                title="Range"
                elementsController={datesController}
            />
            <p className="error">{ errMessage !== "" ? errMessage : null }</p>
            <div className="d-flex flex-wrap align-items-center filter-form-row">
                <div className="title">Action</div>
                <div className="content">
                    <button 
                        className="btn btn-light"
                        type="submit"
                        onClick={handleSubmit}
                    >
                        Submit
                    </button>
                    <button 
                        className="btn btn-light"
                        onClick={resetFilterFormFields}
                    >
                        Reset
                    </button>
                    <button 
                        className="btn btn-light"
                        onClick={cancelChanges}
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </form>
    );
}

export default FilterForm;
