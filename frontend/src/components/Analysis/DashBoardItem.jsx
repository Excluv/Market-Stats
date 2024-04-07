import { Chart as CustomChart } from "react-chartjs-2";
import { 
  Chart as ChartModule, 
  registerables  
} from "chart.js";
ChartModule.register(...registerables);


// --- Util components ---
function TableBody(props) {
  const rows = Object.entries(props.body).map(([key, value]) => {
    return value;
  }).map((object) => {
    const values = Object.entries(object).map(([objKey, objValue]) => {
      return objValue;
    })
    return (
      <tr key={`table-row-${1}`} className="rounded-3">
        <th scope="row">{values[0]}</th>
        <td>{values[1]}</td>
        <td>{values[2]}</td>
        <td>{values[3]}</td>
      </tr>
    );
  });

  return (
    <tbody>{rows}</tbody>
  );
}

function TableHeader(props) {
  const headerCompsList = props.header.map((header, index) => 
    <th key={index} scope="col">{header}</th>
  );
  return (
    <thead>
      <tr>
        {headerCompsList}
      </tr>
    </thead>
  );
}

export function Table(props) {
  return (
    <div className="statistics">
      <table className="table bg-dark table-striped table-hover p-2">
        <TableHeader header={props.header} />
        <TableBody body={props.body} />
      </table>
    </div>
  );
}

export function Chart(props) {
  return (
    <CustomChart data={props.chartData} options={props.options} />
  );
}

// Needs rework
export function SummaryDiv(props) {
  return (
    <>
      <p className="text-start text-uppercase summary-title"><b>{props.title}</b></p>
      <p className="summary-content">{props.summary}</p>
      <p className="text-start summary-description">{props.content}</p>
    </>
  );
}

export function Tabs(props) {
  const listItemComps = props.items.map((object, index) => 
    <li className="nav-item" key={`tab-item-${index}`}>
      <a href="" 
        className={`nav-link ${props.selection.title === object.title ? "active" : ""}`}
        onClick={(event) => {
          event.preventDefault();
          props.setSelection(object);
        }}
      >
        {object.title}
      </a>
    </li>
  )
  return (
    <ul className="nav nav-tabs">
      {listItemComps}
    </ul>
  );
}

export function Pills(props) {
  const listItemComps = props.items.map((object, index) => 
    <li className="nav-item" key={`pill-item-${index}`}>
      <a href="" 
        className={`nav-link ${props.selection.title === object.title ? "active" : ""}`}
        onClick={(event) => {
          event.preventDefault();
          props.setSelection(object);
        }}
      >
        {object.title}
      </a>
    </li>
  );
  return (
    <ul className="nav nav-pills nav-fill">
      {listItemComps}
    </ul>
  );
}
// --- End util components section ---

// --- Major - or wrapper components ---
export function ScrollableColumn(props) {
  return (
    <div className="m-0 col p-2 col-sm-4 scrollable-outer">
      <div className="m-0 p-3 scrollable">
        {props.childComponent}
      </div>
    </div>
  );
}

export function Column(props) {
  const columnClass = 
    "m-0 col p-2 " + (props.config.columnSize ? `col-sm-${props.config.columnSize}` : "");
  const contentClass = 
    "border rounded-2 " 
      + (props.config.columnHeight ? `h-${props.config.columnHeight} ` : " ")
      + (props.config.contentPadding ? `p-${props.config.contentPadding} ` : " ");

  return (
    <div className={columnClass}>
      <div className={contentClass}>
        {props.childComponent}
      </div>
    </div>
  );
}

export function Row(props) {
  const rowClass = 
    "row rounded-3 " + 
    (props.config.rowHeight ? `h-${props.config.rowHeight}` : "") + 
    " " +
    (props.config.rowWidth ? `h-${props.config.rowWidth}` : "");

  return (
    <div className={rowClass}>
      {props.childComponent}
    </div>
  );
}



