// Chart heights
export const SmallChartHeight = { height: 300 };
export const BigChartHeight = { height: 400 };

// Chart widths
export const SmallChartConfig = { 
  columnSize: "3",
  contentPadding: "3"
};
export const MediumChartConfig = { 
  columnSize: "4",
  contentPadding: "3"
};
export const BigChartConfig = { 
  columnSize: "8",
  contentPadding: "3"
};

// Table component config
export const SmallTableConfig = {
  columnSize: "2",
}
export const MediumTableConfig = {
  columnSize: "3",
}
export const BigTableConfig = {
  columnSize: "4",
  columnHeight: "100",
  contentPadding: "2",
}

// Row component config
export const RowConfig = {
  rowWidth: false,
  rowHeight: false,
};


// Construct chart configs from a given dataset
export function getChartConfig(DataArray, product) {
  const chartData = new Array();
  const chartScales = new Array();

  // Line chart config
  const lineWidth = 2;

  // Loops through the array to get a different config for each chart
  DataArray.forEach((dataset) => {
    const chartDatasets = new Array();
    const yScales = {};
    let xAxisLabels = null;

    Object.entries(dataset).forEach(([key, value], index) => {
      if (key === "date") {
        xAxisLabels = value;
      }
      else {
        yScales[`y-${index}`] = {
          position: index === 1 ? "left" : "right",
          grid: { display: false },
        }
        
        chartDatasets.push({
          type: "line",
          fill: key === product ? true : false,
          label: key.split("_").join(" "),
          data: value,
          borderWidth: lineWidth,
          yAxisID: `y-${index}`,
        });
      }
    });

    chartData.push({ labels: xAxisLabels, datasets: chartDatasets });
    chartScales.push(yScales);
  });

  return { chartData: chartData, chartScales: chartScales };
}


// Sets chart options from the given parameters
export function getChartOptions(title, scales) {
  const chartConfig = {
    maintainAspectRatio: false,
    radius: 0,
    interaction: {
      intersect: false,
      mode: "index",
    },
    plugins: {
      colors: {
        enabled: true,
        forceOverride: true,
      },
      title: {
        display: true,
        text: title,
        font: { size: 18 }
      },
      legend: {
        align: "center",
        position: "top",
        labels: {
          boxHeight: 7,
          usePointStyle: true,
        },
      }
    },
    scales: scales,
  }

  return chartConfig;
}
