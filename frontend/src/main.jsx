// Styling Files
import "bootstrap/dist/css/bootstrap.css";
import "./index.css";

// Root Components
import Header from "./components/Header";
import Footer from "./components/Footer";
import RankingTable from "./components/RankingTable";
import Analysis, {
  loader as productLoader
} from "./components/Analysis";

// Child Components
import ErrorPage from "./components/Analysis/Error";
import DashBoard, {
  loader as contentLoader
} from "./components/Analysis/DashBoard";

import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, Outlet, RouterProvider } from "react-router-dom";


const router = createBrowserRouter([
  {
    element: (
      <>
        <Header />
        <main>
          <Outlet />
        </main>
        <Footer />
      </>
    ),
    children: [
      {
        path: "/",
        element: <RankingTable />,
      },
      {
        path: "analysis/:product",
        element: <Analysis />,
        loader: productLoader,
        children: [
          {
            errorElement: <ErrorPage />,
            children: [
              {
                path: ":sector/",
                element: <DashBoard />,
                loader: contentLoader,
              },
            ]
          },
        ]
      },
    ]
  }
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router}/>
  </React.StrictMode>
);
