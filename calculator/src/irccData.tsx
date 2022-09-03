import { Decimal } from "decimal.js";
import irccJSONData from "../../historical-data/ircc.json";
import { IrccDailyEntry, IrccQuarterlyEntry } from "./types";

const irccDailyData: Array<IrccDailyEntry> = irccJSONData
  .map((p: any) => ({ rate: p.rate, date: new Date(p.date) }))
  .sort((a, b) => a.date.getTime() - b.date.getTime());

// Compute an object that contains the quarter as key and the list of coresponding daily entries as value
const irccDataByQuarter: { [key: string]: Array<IrccDailyEntry> } =
  irccDailyData.reduce((prev, irccDailyEntry) => {
    const quarter = Math.floor(irccDailyEntry.date.getUTCMonth() / 3) + 1;
    const year = irccDailyEntry.date.getUTCFullYear();
    const yearQuarter = `${year}-T${quarter}`;
    prev[yearQuarter] = (prev[yearQuarter] || []).concat([irccDailyEntry]);
    return prev;
  }, {});

// Compute the list of the ircc date. This shouuld correspond with the
// list from https://www.bnr.ro/Indicele-de-referin%C8%9Ba-pentru-creditele-consumatorilor--19492-Mobile.aspx
// I used decimal.js because the floating point operations in JS are not precise enough.
const irccQuarterData: Array<IrccQuarterlyEntry> = Object.values(
  irccDataByQuarter
).map((quarterIrccData) => {
  const totalSum = quarterIrccData.reduce(
    (prev, current) => prev.add(new Decimal(current.rate)),
    new Decimal(0)
  );
  return {
    rate: totalSum
      .div(quarterIrccData.length)
      .toFixed(2, Decimal.ROUND_HALF_UP),
    startDate: quarterIrccData[0].date,
    endDate: quarterIrccData.slice(-1)[0].date,
  };
});

export { irccDailyData, irccQuarterData };
