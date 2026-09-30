import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';

export default function DapGrowthCurve() {
  // Generate 40 Days After Planting (DAP) growth trajectory data
  const data = Array.from({ length: 40 }, (_, i) => {
    const dap = i + 1;
    // Sigmoidal/Gaussian uptake growth trajectory over crop lifespan
    const k_uptake = 20 + 55 / (1 + Math.exp(-(dap - 22) / 4.5));
    const mg_uptake = 18 + 48 / (1 + Math.exp(-(dap - 20) / 5.0));
    const n_uptake = 22 + 52 / (1 + Math.exp(-(dap - 21) / 4.2));

    return {
      dap: `DAP ${dap}`,
      dap_val: dap,
      'K System': Number(k_uptake.toFixed(2)),
      'Mg System': Number(mg_uptake.toFixed(2)),
      'N System': Number(n_uptake.toFixed(2)),
    };
  });

  return (
    <section className="dark-panel">
      <div className="lighter-green-subheading">GROWTH STAGE TRAJECTORY (PAPER FIG. 2)</div>
      <h3 style={{ fontFamily: 'var(--font-heading)', color: '#ffffff', marginBottom: '0.5rem', fontSize: '1.25rem' }}>
        Daily Water Uptake vs. Days After Planting (DAP 1–40)
      </h3>
      <p style={{ color: '#c4d4c0', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
        Soybean daily evapotranspiration and water consumption trajectory across vegetative, flowering, and pod-filling growth stages under K, Mg, and N nutrient regimes.
      </p>

      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#38592f" opacity={0.4} />
            <XAxis
              dataKey="dap_val"
              stroke="#8aa384"
              tick={{ fill: '#8aa384', fontSize: 12 }}
              label={{ value: 'Days After Planting (DAP)', position: 'insideBottom', offset: -5, fill: '#8aa384', fontSize: 12 }}
            />
            <YAxis
              stroke="#8aa384"
              tick={{ fill: '#8aa384', fontSize: 12 }}
              label={{ value: 'Water Uptake (mL/day)', angle: -90, position: 'insideLeft', fill: '#8aa384', fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1b3317',
                borderColor: '#38592f',
                borderRadius: '8px',
                color: '#ffffff',
                fontFamily: 'var(--font-heading)'
              }}
            />
            <Legend wrapperStyle={{ fontFamily: 'var(--font-heading)', fontSize: '13px' }} />
            <Line type="monotone" dataKey="K System" stroke="#8cc63f" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
            <Line type="monotone" dataKey="Mg System" stroke="#7ea373" strokeWidth={2.5} strokeDasharray="5 5" dot={false} />
            <Line type="monotone" dataKey="N System" stroke="#e5e0d1" strokeWidth={2.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
