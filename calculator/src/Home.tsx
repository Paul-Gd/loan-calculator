import React from "react";

import "./Home.css";
import { irccDailyData } from "./irccData";

import { DailyIrccLineChart } from "./charts/DailyIrccLineChart";
import { QuarterIrccBarChart } from "./charts/QuarterIrccBarChart";

class Home extends React.Component<{}, {}> {
  public render() {
    return (
      <div className="home-chart">
        <QuarterIrccBarChart />
        <DailyIrccLineChart />
      </div>
    );
  }
}

export default Home;
