"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type SalaryTrendChartProps = {
  data: { date: string; value: number }[];
};

export function SalaryTrendChart({ data }: SalaryTrendChartProps) {
  const formatted = data.map((d) => ({ ...d, label: d.date }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={formatted} margin={{ left: 12, right: 12, top: 8 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis dataKey="label" tick={{ fontSize: 12 }} className="fill-muted-foreground" />
        <YAxis
          tick={{ fontSize: 12 }}
          className="fill-muted-foreground"
          tickFormatter={(v: number) => `$${Math.round(v / 1000)}k`}
        />
        <Tooltip
          formatter={(value) => [`$${Number(value).toLocaleString()}`, "Salary"]}
          labelFormatter={(label) => `Date: ${label}`}
        />
        <Line
          type="monotone"
          dataKey="value"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          dot={{ r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

type WaterfallDatum = {
  name: string;
  start: number;
  end: number;
  contribution: number;
  isTotal: boolean;
};

type WaterfallChartProps = {
  baseValue: number;
  predictedValue: number;
  contributions: { feature: string; contribution: number }[];
};

export function WaterfallChart({
  baseValue,
  predictedValue,
  contributions,
}: WaterfallChartProps) {
  const top = contributions
    .slice()
    .sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution))
    .slice(0, 8);

  let running = baseValue;
  const data: WaterfallDatum[] = [
    { name: "Base value", start: 0, end: baseValue, contribution: baseValue, isTotal: true },
  ];
  for (const c of top) {
    data.push({
      name: c.feature.length > 18 ? `${c.feature.slice(0, 17)}…` : c.feature,
      start: running,
      end: running + c.contribution,
      contribution: c.contribution,
      isTotal: false,
    });
    running += c.contribution;
  }
  data.push({
    name: "Prediction",
    start: running,
    end: predictedValue,
    contribution: predictedValue - running,
    isTotal: true,
  });

  const maxAbs = Math.max(
    ...data.map((d) => Math.abs(d.contribution)),
    Math.abs(predictedValue - baseValue),
  );

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ left: 12, right: 12, top: 8 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} className="fill-muted-foreground" interval={0} />
        <YAxis
          tick={{ fontSize: 12 }}
          className="fill-muted-foreground"
          domain={[baseValue - maxAbs, predictedValue + maxAbs]}
          tickFormatter={(v: number) => `$${Math.round(v / 1000)}k`}
        />
        <Tooltip
          formatter={(value) => [`$${Math.round(Number(value)).toLocaleString()}`, "Salary"]}
        />
        <Bar dataKey="start" stackId="a" fill="transparent" />
        <Bar dataKey="end" stackId="a" name="contribution">
          {data.map((entry, idx) => (
            <Cell
              key={idx}
              fill={entry.isTotal ? "hsl(var(--primary))" : entry.contribution >= 0 ? "#10b981" : "#ef4444"}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

type TopSkillsBarChartProps = {
  data: { skill: string; count: number }[];
};

export function TopSkillsBarChart({ data }: TopSkillsBarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(160, data.length * 28)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ left: 12, right: 24, top: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" horizontal={false} />
        <XAxis type="number" className="fill-muted-foreground" tick={{ fontSize: 12 }} />
        <YAxis
          type="category"
          dataKey="skill"
          width={120}
          tick={{ fontSize: 12 }}
          className="fill-muted-foreground"
        />
        <Tooltip
          formatter={(value) => [String(value), "Occurrences"]}
        />
        <Bar dataKey="count" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
