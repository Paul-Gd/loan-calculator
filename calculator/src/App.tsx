import React from "react";
import { Route, Switch } from "react-router-dom";
import Home from "./Home";

import "./App.css";

const App = () => (
  <Switch>
    <Route exact={true} path={`${process.env.PUBLIC_PATH}`} component={Home} />
    <Route component={() => <div>Route not found!</div>} />
  </Switch>
);

export default App;
