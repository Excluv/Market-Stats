import { Link } from "react-router-dom";


export default function Sector(props) {
  const itemsList = [
    // "Business Survey", 
    // "Consumer Survey", 
    // "Employment", 
    // "Growth", 
    // "Housing", 
    // "Inflation", 
    "Money and Interest Rate",
  ].map((element, index) => {
    const className = "list-group-item list-group-item-action";

    return (
      <Link 
        to={`${element}`}
        key={`listitem-${index}`} 
        className={ props.sectorSelection === element ? className + " active" : className }
        onClick={() => props.setSectorSelection(element)}
      >
        {element}
      </Link>
    );
  });

  return (
    <>{itemsList}</>
  );
}
