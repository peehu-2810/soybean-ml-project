import React, { useState } from 'react';

const COMPOUND_ROLES = {
  Mn: "Manganese: Essential for photosynthesis electron transport and root oxidation defense.",
  TDS: "Total Dissolved Solids: Governs root osmotic gradient driving water entry.",
  SO4: "Sulfate: Supplies sulfur for root protein synthesis & ionic equilibrium.",
  "NO3-N": "Nitrate-N: Directly activates root aquaporin channels & hydraulic flow.",
  Alkalinity: "Alkalinity: Maintains optimal root zone pH for nutrient solubility.",
  Na: "Sodium: Regulates cellular turgor pressure and transpiration pathways.",
  P: "Phosphorus: Powers cellular ATP energy required for ion trans-membrane uptake.",
  Ca: "Calcium: Maintains root cell wall integrity and selective membrane transport.",
  Hardness: "Hardness: Measures Ca²⁺ + Mg²⁺ cation pool influencing cell wall elasticity.",
  CO3: "Carbonate: Carbonate ion buffer regulating root microenvironment stability.",
  HCO3: "Bicarbonate: Bicarbonate exchange mechanism balancing cell respiration.",
  K: "Potassium: Major cellular osmolyte controlling guard cell stomatal closure."
};

export default function ShapSection({ shapData }) {
  const [activeNutrientTab, setActiveNutrientTab] = useState('K');

  const nutrientShap = shapData[activeNutrientTab] || {};
  const importanceList = nutrientShap.importance || [];
  const maxShap = importanceList.length > 0 ? Math.max(...importanceList.map(i => i.mean_absolute_shap)) : 1;

  return (
    <section className="dark-panel">
      <div className="lighter-green-subheading">MODEL EXPLAINABILITY & SHAP FEATURE IMPORTANCE</div>
      <p style={{ color: '#c4d4c0', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
        Model-agnostic SHAP (SHapley Additive exPlanations) values quantifying the exact contribution of each chemical factor to predicted water uptake.
      </p>

      {/* SHAP Tabs */}
      <div className="tabs-header" style={{ marginBottom: '1.25rem' }}>
        {['K', 'Mg', 'N'].map((nut) => (
          <button
            key={nut}
            className={`tab-button ${activeNutrientTab === nut ? 'active' : ''}`}
            onClick={() => setActiveNutrientTab(nut)}
            style={{ padding: '0.4rem 1.25rem', fontSize: '0.85rem' }}
          >
            {nut} FEATURE IMPACT
          </button>
        ))}
      </div>

      <div className="shap-grid">
        {/* SHAP Impact Progress Bars */}
        <div>
          {importanceList.map((item) => {
            const val = item.mean_absolute_shap;
            const pct = (val / maxShap) * 100;

            return (
              <div key={item.feature} className="shap-item">
                <div className="shap-item-header">
                  <span>{item.feature}</span>
                  <span style={{ color: 'var(--color-vibrant-green)', fontFamily: 'var(--font-heading)', fontWeight: '700' }}>
                    {val.toFixed(2)}
                  </span>
                </div>
                <div className="shap-bar-track">
                  <div className="shap-bar-fill" style={{ width: `${pct}%` }}></div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Compound Scientific Role Descriptions */}
        <div>
          <div className="lighter-green-subheading" style={{ fontSize: '0.8rem', marginBottom: '0.75rem' }}>
            TOP CHEMICAL FACTORS
          </div>
          {importanceList.slice(0, 5).map((item) => (
            <div key={item.feature} style={{ marginBottom: '0.85rem', fontSize: '0.85rem', lineHeight: '1.4' }}>
              <strong style={{ color: 'var(--color-vibrant-green)' }}>{item.feature}: </strong>
              <span style={{ color: '#d0d7ce' }}>
                {COMPOUND_ROLES[item.feature] || "Key hydroponic chemical constituent."}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
