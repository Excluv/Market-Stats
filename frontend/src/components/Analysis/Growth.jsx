// React hooks
import { useState, useEffect } from "react";

// Charting utils
import { 
  getChartConfig, getChartOptions,
  SmallTableConfig, MediumTableConfig, RowConfig,
  SmallChartHeight, BigChartHeight, 
  SmallChartConfig, MediumChartConfig, BigChartConfig, 
} from "./Config";

// Child Components
import { 
  MyChart, Row, Column, 
  Table, ScrollableColumn, SummaryDiv
} from "./DashBoardItem";


export default function Growth(props) {
  // Constructs charts data and their scales
  const [chartData, setChartData] = useState();
  const [chartScales, setChartScales] = useState();
  useEffect(() => {
    if (props.data) {
      try {
        const DataArray = [
          props.data["price_mixed_set"],
          props.data["news_mixed_set_1"],
          props.data["news_mixed_set_2"],
          props.data["news_mixed_set_3"]
        ];
        const chartConfig = getChartConfig(DataArray);
        setChartData(chartConfig.chartData);
        setChartScales(chartConfig.chartScales);
      }
      catch {
        // Data is temporary of the wrong format due to the delay in update, so that when we try 
        // to loop over the specified array, some elements won't be there, thus we can skip the error
        // raised while looping and let the new dataset be updated into the current one
      }
    }
  }, [props.data]);

  // Constructs display components
  const [rowComps, setRowComps] = useState();
  useEffect(() => {
    if (chartData) {
      const chartComps = chartData.map((chartObject, index) => {
        return (
          <Column 
            key={`chart-column-${index + 1}`}
            config={BigChartConfig}
            childComponent={
              <div 
                key={`line-chart-${index + 1}`} 
                style={BigChartHeight}
              >
                <MyChart
                  chartData={chartObject} 
                  options={
                    getChartOptions("Something", chartScales[index])
                  } 
                />
              </div>
            }
          />
        );
      });
      
      const tableComps = chartData.map((chartObject, index) => {
          if (index === 0) {
            return (
              <ScrollableColumn 
                key={`scrollable-${index}`}
                childComponent={[
                  (
                    <Table
                      key={`table-${1}`}
                      content={{
                        title: "Summary Table",
                        head: ["#", "Metric", "Value"],
                        body: [
                          { name: "Correlation", value: "Value" },
                          { name: "Something", value: "Value" },
                        ],
                      }}
                    />
                  ),
                  (
                    <Table
                      key={`table-${2}`}
                      content={{
                        title: "Summary Table",
                        head: ["#", "Metric", "Value"],
                        body: [
                          { name: "Correlation", value: "Value" },
                          { name: "Something", value: "Value" },
                        ],
                      }}
                    />
                  )
                ]}
              />
            )
          }
          else {
            return (
              <Column 
                key={`chart-column-${index + 3}`}
                config={MediumTableConfig}
                childComponent={[
                  (
                    <Table
                      key={`table-${1}`}
                      content={{
                        title: "Summary Table",
                        head: ["#", "Metric", "Value"],
                        body: [
                          { name: "Correlation", value: "Value" },
                          { name: "Something", value: "Value" },
                        ],
                      }}
                    />
                  ),
                  (
                    <SummaryDiv
                      key={`summary-${1}`} 
                      title={"Something"}
                      content={"Something else"}
                    />
                  )
                ]}
              />
            )
          }
        }
      );

      setRowComps([
        <Row 
            key={`row-${1}`} 
            config={RowConfig} 
            childComponent={[chartComps[0], tableComps[0]]} 
        />,
        <Row 
          key={`row-${2}`} 
          config={RowConfig} 
          childComponent={[tableComps[1], chartComps[1]]} 
        />, 
        <Row 
          key={`row-${3}`} 
          config={RowConfig} 
          childComponent={[chartComps[2], tableComps[2]]} 
        />, 
        <Row 
          key={`row-${4}`} 
          config={RowConfig} 
          childComponent={[tableComps[3], chartComps[3]]} 
        />, 
      ]);
    }
  }, [chartData]);
  
  return (
    <>
      {rowComps ? rowComps : <></>}
    </>
  );
}