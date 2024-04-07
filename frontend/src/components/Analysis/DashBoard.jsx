// React hooks
import { useState, useEffect } from "react";

// React router 
import { useLoaderData } from "react-router-dom";

// Child component
// import ConsumerSurvey from "./ConsumerSurvey";
// import Employment from "./Employment";
// import Growth from "./Growth";
// import Inflation from "./Inflation";
import InterestRate from "./InterestRate";

// Util function
import { fetchData } from "./utils";


export function loader({ params }) {
  const query = {
    product: params.product,
    sector: params.sector,
  };
  return query;
}

export default function DashBoard() {
  const query = useLoaderData();
  const [data, setData] = useState();

  useEffect(() => {    
    const URL = `http://localhost:8000/analysis/product=${query.product}/sector=${query.sector}`;
    fetchData(URL, setData);
  }, [query]);

  const contentMapping = {
    // "Consumer Survey": <ConsumerSurvey data={data} product={query.product} />,
    // "Employment": <Employment data={data} product={query.product} />,
    // "Growth": <Growth data={data} product={query.product} />,
    // "Inflation": <Inflation data={data} product={query.product} />,
    "Money and Interest Rate": <InterestRate data={data} product={query.product} />,
  };

  return (
    contentMapping[query.sector]
  );
}