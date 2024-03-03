import TableRow from "./TableRow";
 

function TableBody(props) {
    const rowComps = props.data.map((object) => 
        <TableRow 
            key={object.id}
            id={object.id}
            object={object}
            filterParams={props.filterParams}
        />
    );
    
    return (
        <tbody className="table-group-divider">
            {rowComps}
        </tbody>
    );
}

export default TableBody;
