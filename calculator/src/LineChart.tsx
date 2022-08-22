import React, { useEffect, useState } from "react";
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
  Legend
);

export const LineChart = (props: Props) => {
  const [zoomLoaded, setZoomLoaded] = useState(false);
  useEffect(() => {
    if (process.env.BUILD_TARGET === "client") {
      // chartjs-plugin-zoom uses handlebarsjs. At import, handlebarsjs expects window to be present but
      // on server, there is no window so the ssr crashes
      import("chartjs-plugin-zoom").then((zoomPlugin) => {
        ChartJS.register(zoomPlugin.default);
        setZoomLoaded(true);
      });
    }
  }, [setZoomLoaded]);
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
      {zoomLoaded ? <Line options={options} data={data} /> : "Loading chart!"}
    </div>
  );
};
