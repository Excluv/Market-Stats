// React hook
import { useState } from "react";

// React Router Components
import { Outlet, useLoaderData } from "react-router-dom";

// Child Components
import Sector from "./Analysis/Sector";


export function loader({ params }) {
  return {
    product: params.product,
    sector: params.sector
  };
}

export default function Analysis() {
  const query = useLoaderData();
  const [sectorSelection, setSectorSelection] = useState(query.sector);

  return (
    <div className="container-fluid analysis rounded-3 p-3">
      <div className="left-section p-3">
        <h5>{query.product}</h5>
        <hr/>
        <h5>Indicators</h5>
        <hr/>
        <div className="list-group">
          <p className="m-0 text-start">Economics Overview</p>
          <Sector 
            sectorSelection={sectorSelection}
            setSectorSelection={setSectorSelection} 
          />
        </div>
        <div className="list-group">
          <p className="m-0 text-start">Product Statistics</p>
          <a href="#" className="list-group-item list-group-item-action">Summary</a>
        </div>
      </div>
      <div className="container-fluid right-section p-2">
        <Outlet />
      </div>
    </div>
  );
}
