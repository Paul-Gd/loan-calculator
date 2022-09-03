import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { irccQuarterData } from "../irccData";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const getTitle = (title, index) => {
  switch (irccQuarterData.length - index) {
    case 2:
      return `${title} - Date neoficiale`;
    case 1:
      return `${title} - Date incomplete bazate pe indicele zilnic pana in data de ${irccQuarterData
        .slice(-1)[0]
        .endDate.toLocaleDateString()}`;
    default:
      return title;
  }
};

export const options: ChartOptions<"bar"> = {
  responsive: true,
  plugins: {
    legend: {
      position: "top" as const,
    },
    title: {
      display: true,
      text: "Indice IRCC trimestrial",
    },
    tooltip: {
      callbacks: {
        title: (e) => getTitle(e[0].label, e[0].dataIndex),
      },
    },
  },
};

const labels = irccQuarterData.map(
  (e) => `${e.startDate.getUTCFullYear()}T${e.startDate.getUTCMonth() / 3 + 1}`
);

const barsBackgroundColor = irccQuarterData.map((_, dataIndex) => {
  switch (irccQuarterData.length - dataIndex) {
    case 2:
      return "rgba(53, 162, 235, 0.7)";
    case 1:
      return "rgba(53, 162, 235, 0.3)";
    default:
      return "rgba(53, 162, 235, 1)";
  }
});

const data = {
  labels,
  datasets: [
    {
      label: "Indice trimestrial",
      data: irccQuarterData.map((e) => e.rate),
      backgroundColor: barsBackgroundColor,
    },
  ],
};

export const QuarterIrccBarChart = () => {
  return <Bar options={options} data={data} />;
};
