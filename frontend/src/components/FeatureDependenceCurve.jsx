import React, { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

export default function FeatureDependenceCurve() {
  const [selectedFeature, setSelectedFeature] = useState('TDS');

  // Concentration dependence curves matching Paper Fig. 6 saturation dynamics
  const generateDependenceData = (feature) => {
    return Array.from({ length: 25 }, (_, i) => {
      let conc = 0;
      let uptake = 0;

      if (feature === 'TDS') {
        conc = 500 + i * 16;
        // Saturation curve: initial rapid increase, then plateauing at high ionic strength
        uptake = 25 + 50 * (1 - Math.exp(-0.006 * (conc - 480)));
      } else if (feature === 'Mn') {
        conc = 0.18 + i * 0.005;
        uptake = 30 + 45 * Math.sin((conc - 0.18) * 12);
      } else if (feature === 'P') {
        conc = 0.35 + i * 0.015;
        uptake = 35 + 40 * (1 - Math.exp(-6 * (conc - 0.35)));
      }

      return {
        concentration: Number(conc.toFixed(2)),
        predicted_uptake: Number(Math.max(0, uptake).toFixed(2))
      };
    });
  };

  const currentData = generateDependenceData(selectedFeature);

  return (
    <section className="dark-panel">
      <div className="lighter-green-subheading">SHAP DEPENDENCE & SATURATION CURVE (PAPER FIG. 6)</div>
      <h3 style={{ fontFamily: 'var(--font-heading)', color: '#ffffff', marginBottom: '0.5rem', fontSize: '1.25rem' }}>
        Concentration Saturation Impact Curve ({selectedFeature})
      </h3>
      <p style={{ color: '#c4d4c0', marginBottom: '1.25rem', fontSize: '0.9rem' }}>
        Non-linear response curve demonstrating how chemical concentration (ppm) of primary drivers regulates soybean water uptake capacity.
      </p>

      {/* Feature Selector Pills */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
        {['TDS', 'Mn', 'P'].map((feat) => (
          <button
            key={feat}
            className={`preset-button ${selectedFeature === feat ? 'active' : ''}`}
            onClick={() => setSelectedFeature(feat)}
            style={{
              backgroundColor: selectedFeature === feat ? 'var(--color-vibrant-green)' : '#1b3317',
              color: selectedFeature === feat ? 'var(--bg-dark-hero)' : '#ffffff',
              border: '1px solid var(--border-green)',
              fontFamily: 'var(--font-heading)',
              fontWeight: '700'
            }}
          >
            {feat} DEPENDENCE
          </button>
        ))}
      </div>

      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={currentData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
            <defs>
              <linearGradient id="colorUptake" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8cc63f" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#8cc63f" stopOpacity={0.05}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#38592f" opacity={0.4} />
            <XAxis
              dataKey="concentration"
              stroke="#8aa384"
              tick={{ fill: '#8aa384', fontSize: 12 }}
              label={{ value: `${selectedFeature} Concentration (ppm)`, position: 'insideBottom', offset: -5, fill: '#8aa384', fontSize: 12 }}
            />
            <YAxis
              stroke="#8aa384"
              tick={{ fill: '#8aa384', fontSize: 12 }}
              label={{ value: 'Predicted Uptake (mL/day)', angle: -90, position: 'insideLeft', fill: '#8aa384', fontSize: 12 }}
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
            <Area type="monotone" dataKey="predicted_uptake" stroke="#8cc63f" strokeWidth={3} fillOpacity={1} fill="url(#colorUptake)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
