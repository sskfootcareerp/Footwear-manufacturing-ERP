import { useEffect, useState } from "react";
import { http, inr, num } from "../lib/api";
import { PageHeader, Card, Badge } from "../components/ui-kit";
import { TrendingUp, Clock, AlertOctagon } from "lucide-react";

export default function Reports() {
  const [tab, setTab] = useState("variance");
  const [variance, setVariance] = useState([]);
  const [cycle, setCycle] = useState([]);
  const [defects, setDefects] = useState(null);

  useEffect(() => {
    http.get("/reports/cost-variance").then(r => setVariance(r.data)).catch(() => {});
    http.get("/reports/stage-cycle-time").then(r => setCycle(r.data)).catch(() => {});
    http.get("/reports/defect-rate").then(r => setDefects(r.data)).catch(() => {});
  }, []);

  const tabs = [
    { key: "variance", label: "Cost Variance", icon: TrendingUp },
    { key: "cycle", label: "Stage Cycle Time", icon: Clock },
    { key: "defects", label: "Defect Rate", icon: AlertOctagon },
  ];

  return (
    <div>
      <PageHeader title="Reports" subtitle="Analytics / Reports" testId="reports-header" />

      <div className="p-8">
        <div className="flex border-b-2 border-slate-200 mb-6">
          {tabs.map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              data-testid={`tab-${t.key}`}
              className={`px-5 py-3 text-xs font-bold uppercase tracking-wider border-b-4 -mb-0.5 transition-colors flex items-center gap-2 ${
                tab === t.key ? "border-[#C27842] text-slate-900" : "border-transparent text-slate-500 hover:text-slate-900"
              }`}
            >
              <t.icon className="w-4 h-4" /> {t.label}
            </button>
          ))}
        </div>

        {tab === "variance" && <VarianceReport rows={variance} />}
        {tab === "cycle" && <CycleReport rows={cycle} />}
        {tab === "defects" && <DefectReport data={defects} />}
      </div>
    </div>
  );
}

function VarianceReport({ rows }) {
  if (!rows.length) return <Empty label="No variance data — add Styles and POs to see cost variance." />;
  return (
    <Card className="overflow-hidden">
      <div className="px-5 py-3 border-b-2 border-slate-200 flex items-baseline justify-between">
        <h2 className="text-sm font-bold uppercase tracking-wider">PO Margin vs Computed Cost</h2>
        <span className="text-[10px] uppercase tracking-wider text-slate-500">Sorted by margin (worst first)</span>
      </div>
      <table className="w-full text-sm" data-testid="variance-table">
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr className="text-left text-[10px] uppercase tracking-wider text-slate-600">
            <th className="px-4 py-2 font-bold">PO</th>
            <th className="px-4 py-2 font-bold">Client</th>
            <th className="px-4 py-2 font-bold">Style</th>
            <th className="px-4 py-2 font-bold text-right">Qty</th>
            <th className="px-4 py-2 font-bold text-right">Computed</th>
            <th className="px-4 py-2 font-bold text-right">PO Price</th>
            <th className="px-4 py-2 font-bold text-right">Margin</th>
            <th className="px-4 py-2 font-bold text-right">Margin %</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => {
            const color = r.margin_pct < 0 ? "red" : r.margin_pct < 10 ? "yellow" : "green";
            return (
              <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-2 font-mono text-xs font-bold">{r.po_number}</td>
                <td className="px-4 py-2 text-xs">{r.client}</td>
                <td className="px-4 py-2 font-mono text-xs">{r.style_code}</td>
                <td className="px-4 py-2 text-right font-mono">{r.quantity}</td>
                <td className="px-4 py-2 text-right font-mono">{inr(r.computed_cost)}</td>
                <td className="px-4 py-2 text-right font-mono">{inr(r.po_unit_price)}</td>
                <td className="px-4 py-2 text-right font-mono">{inr(r.variance)}</td>
                <td className="px-4 py-2 text-right"><Badge color={color}>{num(r.margin_pct, 1)}%</Badge></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </Card>
  );
}

function CycleReport({ rows }) {
  if (!rows.length) return <Empty label="No cycle-time data yet — move some production jobs across stages to populate this." />;
  return (
    <Card className="overflow-hidden">
      <div className="px-5 py-3 border-b-2 border-slate-200">
        <h2 className="text-sm font-bold uppercase tracking-wider">Avg time between stage transitions</h2>
      </div>
      <table className="w-full text-sm" data-testid="cycle-table">
        <thead className="bg-slate-50">
          <tr className="text-left text-[10px] uppercase tracking-wider text-slate-600 border-b border-slate-200">
            <th className="px-4 py-2 font-bold">From</th>
            <th className="px-4 py-2 font-bold">To</th>
            <th className="px-4 py-2 font-bold text-right">Samples</th>
            <th className="px-4 py-2 font-bold text-right">Avg (hrs)</th>
            <th className="px-4 py-2 font-bold text-right">Min</th>
            <th className="px-4 py-2 font-bold text-right">Max</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
              <td className="px-4 py-2 uppercase text-xs">{r.from_stage}</td>
              <td className="px-4 py-2 uppercase text-xs">→ {r.to_stage}</td>
              <td className="px-4 py-2 text-right font-mono">{r.samples}</td>
              <td className="px-4 py-2 text-right font-mono font-bold">{num(r.avg_hours, 1)}</td>
              <td className="px-4 py-2 text-right font-mono text-slate-500">{num(r.min_hours, 1)}</td>
              <td className="px-4 py-2 text-right font-mono text-slate-500">{num(r.max_hours, 1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

function DefectReport({ data }) {
  if (!data) return <Empty label="Loading defect data..." />;
  if (!data.totals.total_incidents) return <Empty label="No defects logged. Quality is clean." />;
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <Stat label="Total Incidents" value={data.totals.total_incidents} />
        <Stat label="Total Defective Pairs" value={data.totals.total_defective} />
        <Stat label="Total Cost" value={inr(data.totals.total_cost)} />
      </div>

      <Card className="overflow-hidden">
        <div className="px-5 py-3 border-b-2 border-slate-200"><h2 className="text-sm font-bold uppercase tracking-wider">By Stage</h2></div>
        <table className="w-full text-sm" data-testid="defect-stage-table">
          <thead className="bg-slate-50">
            <tr className="text-left text-[10px] uppercase tracking-wider text-slate-600 border-b border-slate-200">
              <th className="px-4 py-2 font-bold">Stage</th>
              <th className="px-4 py-2 font-bold text-right">Produced</th>
              <th className="px-4 py-2 font-bold text-right">Defective</th>
              <th className="px-4 py-2 font-bold text-right">Rework</th>
              <th className="px-4 py-2 font-bold text-right">Rejected</th>
              <th className="px-4 py-2 font-bold text-right">Cost</th>
              <th className="px-4 py-2 font-bold text-right">Defect %</th>
            </tr>
          </thead>
          <tbody>
            {data.by_stage.map((r, i) => (
              <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-2 uppercase text-xs font-bold">{r.stage}</td>
                <td className="px-4 py-2 text-right font-mono">{r.produced_qty}</td>
                <td className="px-4 py-2 text-right font-mono">{r.defective_qty}</td>
                <td className="px-4 py-2 text-right font-mono">{r.rework_qty}</td>
                <td className="px-4 py-2 text-right font-mono">{r.rejected_qty}</td>
                <td className="px-4 py-2 text-right font-mono">{inr(r.cost)}</td>
                <td className="px-4 py-2 text-right"><Badge color={r.defect_rate_pct > 5 ? "red" : r.defect_rate_pct > 2 ? "yellow" : "green"}>{num(r.defect_rate_pct, 2)}%</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Card className="overflow-hidden">
        <div className="px-5 py-3 border-b-2 border-slate-200"><h2 className="text-sm font-bold uppercase tracking-wider">By Defect Type</h2></div>
        <table className="w-full text-sm" data-testid="defect-type-table">
          <thead className="bg-slate-50">
            <tr className="text-left text-[10px] uppercase tracking-wider text-slate-600 border-b border-slate-200">
              <th className="px-4 py-2 font-bold">Type</th>
              <th className="px-4 py-2 font-bold text-right">Incidents</th>
              <th className="px-4 py-2 font-bold text-right">Defective Qty</th>
              <th className="px-4 py-2 font-bold text-right">Cost</th>
            </tr>
          </thead>
          <tbody>
            {data.by_type.map((r, i) => (
              <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-2"><Badge color="slate">{r.type}</Badge></td>
                <td className="px-4 py-2 text-right font-mono">{r.incidents}</td>
                <td className="px-4 py-2 text-right font-mono font-bold">{r.defective}</td>
                <td className="px-4 py-2 text-right font-mono">{inr(r.cost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <Card className="p-5 relative overflow-hidden">
      <div className="text-[10px] uppercase tracking-[0.2em] font-bold text-slate-500">{label}</div>
      <div className="font-mono text-2xl font-bold mt-2">{value}</div>
      <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-[#C27842]" />
    </Card>
  );
}

function Empty({ label }) {
  return <Card className="p-12 text-center text-slate-400 text-sm">{label}</Card>;
}
