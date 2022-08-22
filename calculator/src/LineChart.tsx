import React from "react";
import { Line } from "react-chartjs-2";

import {
  Chart as ChartJS,
  CategoryScale,
  TimeScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  DateAdapter,
  ChartOptions,
} from "chart.js";
import "chartjs-adapter-date-fns";
import zoomPlugin from "chartjs-plugin-zoom";
import { IrccEntry } from "./types";

export interface Props {
  irccData: Array<IrccEntry>;
}

export const options: ChartOptions<"line"> = {
  scales: {
    x: {
      type: "time",
      time: {
        tooltipFormat: "dd.MM.yyyy",
      },
    },
    y: {
      type: "linear",
      min: 0,
    },
  },
  plugins: {
    zoom: {
      limits: {
        x: { min: "original", max: "original" },
        y: { min: "original", max: "original" },
      },
      zoom: {
        wheel: {
          enabled: true,
        },
        pinch: {
          enabled: true,
        },
        drag: {
          enabled: true,
          modifierKey: "shift",
        },
        mode: "x",
      },
      pan: {
        enabled: true,
        mode: "x",
      },
    },
  },
};

ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  zoomPlugin
);

export const LineChart = (props: Props) => {
  const labels = props.irccData.map((p) => p.date);
  const data = {
    labels,
    datasets: [
      {
        label: "Ircc zilinc",
        data: props.irccData.map((p) => p.rate),
        borderColor: "rgb(53, 162, 235)",
        backgroundColor: "rgba(53, 162, 235, 0.5)",
      },
    ],
  };
  return (
    <div>
      <Line options={options} data={data} />
    </div>
  );
};
