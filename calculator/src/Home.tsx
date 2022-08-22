import React from "react";

import "./Home.css";
import irccData from "./irccData";

import { LineChart } from "./LineChart";

class Home extends React.Component<{}, {}> {
  public render() {
    return (
      <div className="home-chart">
        <LineChart irccData={irccData} />
      </div>
    );
  }
}

export default Home;
