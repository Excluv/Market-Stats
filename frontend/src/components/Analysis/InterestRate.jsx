// React hooks
import { useState, useEffect } from "react";

// React router 
import { useLoaderData } from "react-router-dom";

// Charting utils
import { 
  getChartConfig, getChartOptions,
  BigTableConfig, RowConfig,
  SmallChartHeight, BigChartHeight, 
  SmallChartConfig, BigChartConfig, 
} from "./Config";

// Child Components
import { 
  Chart, Row, Column, 
  Tabs, Pills, Table
} from "./DashBoardItem";

// Util function
import { fetchData } from "./utils";


export default function InterestRate(props) {
  const query = useLoaderData();

  const [chartData, setChartData] = useState();
  const [chartScales, setChartScales] = useState();
  const [chartComps, setChartComps] = useState([]);

  // Get chart data, configs and chart components
  useEffect(() => {
    try {
      const chartDataArray = [
        props.data["price_mixed_set"],
        props.data["news_mixed_set_1"],
        props.data["news_mixed_set_2"],
      ];
      const chartConfig = getChartConfig(chartDataArray, props.product);
      setChartData(chartConfig.chartData);
      setChartScales(chartConfig.chartScales);

      setChartComps(
        chartData.map((chartObject, index) => {
          return (
            <Column 
              key={`chart-column-${index + 1}`}
              config={index === 0 ? BigChartConfig : SmallChartConfig}
              childComponent={
                <div 
                  key={`line-chart-${index + 1}`} 
                  style={index === 0 ? BigChartHeight : SmallChartHeight}
                >
                  <Chart
                    chartData={chartObject} 
                    options={
                      getChartOptions("Something", chartScales[index])
                    } 
                  />
                </div>
              }
            />
          );
        })
      );
    }
    catch {
      // Data is temporary of the wrong format due to the delay in update, so that when we try 
      // to loop over the specified array, some elements won't be there, thus we can skip the error
      // raised while looping and let the new dataset be updated into the current one
    }
  }, [props.data]);
  
  const [tableData, setTableData] = useState({ header: [], body: [] });
  const [period, setPeriod] = useState({ title: "All", query: "20100101-20300101"});
  const [metric, setMetric] = useState({ title: "Correlation", query: "correlation" });

  const periods = [
    { title: "All", query: "20100101-20300101" },
    // { title: "Rate Hike Cycle 2015-2016", query: "20151101-20160101" },
    { title: "Rate Pause Period 2016", query: "20160101-20161101" },
    { title: "Rate Hike Cyle 2016-2017", query: "20161101-20170701" },
    { title: "Rate Pause Period 2017", query: "20170701-20171101" },
    { title: "Rate Hike Cycle 2017-2019", query: "20171101-20190101" },
    { title: "Rate Pause Period 2019", query: "20190101-20190701" },
    { title: "Rate Cut Cycle 2019-2020", query: "20190701-20200401" },
    { title: "Rate Pause Period 2020-2022", query: "20200401-20220201" },
    { title: "Rate Hike Cycle 2022-Present", query: "20220201-20240401" },
  ];
  const metrics = [
    { title: "Correlation", query: "correlation" },
    { title: "Autocorrelation", query: "autocorrelation" },
    { title: "%W Change Distribution", query: "w_relative_change_distribution" },
    { title: "Regression", query: "regression" },
  ]
  
  // Get table data on period and metric selection
  useEffect(() => {
    const URL = 
      "http://localhost:8000/analysis/" +
      `product=${query.product}/sector=${query.sector}/` +
      `period=${period.query}/metric=${metric.query}`;
    fetchData(URL, setTableData);
  }, [chartData, period, metric]);

  return (
    <>
      <Row 
        key={`row-${1}`} 
        config={RowConfig} 
        childComponent={[
          chartComps[0],
          <Column 
            key={"table-column"}
            config={BigTableConfig}
            childComponent={[
              <Pills 
                key={"periods-list"}
                items={periods} 
                selection={period} 
                setSelection={setPeriod} 
              />,
              <Tabs 
                key={"metrics-list"}
                items={metrics} 
                selection={metric} 
                setSelection={setMetric} 
              />,
              <Table 
                header={tableData.header}
                body={tableData.body}
              />
            ]}
          />
        ]} 
      />
      <Row 
        key={`row-${2}`} 
        config={RowConfig} 
        childComponent={[
          chartComps[1], 
          chartComps[2]
        ]} 
      />
    </>
  );
}
