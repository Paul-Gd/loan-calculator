import { renderApp } from "./server";
export const render = (req, res) => {
  const { html } = renderApp(req, res);
  res.json({ html, data: { foo: "bar" } });
};
export const routes = () => {
  return ["/"];
};
