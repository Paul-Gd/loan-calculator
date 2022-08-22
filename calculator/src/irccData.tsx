import irccJSONData from "../../historical-data/ircc.json";
import { IrccEntry } from "./types";

const irccData: Array<IrccEntry> = irccJSONData
  .map((p: any) => ({ rate: p.rate, date: new Date(p.date) }))
  .sort((a, b) => a.date.getTime() - b.date.getTime());

export default irccData;
