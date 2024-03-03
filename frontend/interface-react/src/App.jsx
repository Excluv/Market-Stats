import Header from "./components/Header";
import RankingTable from "./components/RankingTable";
import Footer from "./components/Footer";


function App() {
  const today = new Date(Date.now() - 86400000).toJSON();

  return (
    <>
      <Header />
      <main>
          <div className="container-fluid">
              <div className="row">
                  <h3>Market Update: EOD {`${today.slice(0, 10)}`}</h3>
                  <h5>Investment Product Rankings</h5>
                  <div className="container">
                    <RankingTable />
                  </div>
              </div>
          </div>
      </main>
      <Footer />
    </>
  );
}

export default App;
