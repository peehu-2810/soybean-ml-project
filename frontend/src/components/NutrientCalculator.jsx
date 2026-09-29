import React, { useState, useEffect } from 'react';
import { Target, Eye, Play, Sliders, CheckCircle2 } from 'lucide-react';
import { predictWaterUptake } from '../services/api';

const COMPOUND_DESCRIPTIONS = {
  Ca: "Calcium: Cell wall integrity & membrane permeability",
  Na: "Sodium: Osmotic agent & stomatal regulation",
  SO4: "Sulfate: Protein synthesis & osmotic balance",
  "NO3-N": "Nitrate-Nitrogen: Primary hydraulic conductivity driver",
  P: "Phosphorus: Energy engine driving active trans-membrane transport",
  Alkalinity: "Alkalinity: Root zone pH buffer maintaining ion bioavailability",
  TDS: "Total Dissolved Solids: Overall ionic strength across root membranes",
  Mn: "Manganese: Photosynthesis enzyme & tissue defense activator",
  CO3: "Carbonate: Root zone buffering capacity donor",
  HCO3: "Bicarbonate: Root cell respiration & ion balance agent",
  Hardness: "Total Hardness: Combined Ca + Mg cation concentration",
  K: "Potassium: Osmolyte regulating guard cell turgor & plant water status"
};

export default function NutrientCalculator({ featuresSpecs }) {
  const [activeNutrient, setActiveNutrient] = useState('K');
  const [inputValues, setInputValues] = useState({});
  const [prediction, setPrediction] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const nutrientSpec = featuresSpecs[activeNutrient] || {};
  const featuresList = nutrientSpec.features || [];
  const ranges = nutrientSpec.ranges || {};

  useEffect(() => {
    if (featuresList.length > 0) {
      const initial = {};
      featuresList.forEach(feat => {
        const min = ranges[feat]?.min || 0;
        const max = ranges[feat]?.max || 100;
        initial[feat] = Number(((min + max) / 2).toFixed(2));
      });
      setInputValues(initial);
      runPrediction(activeNutrient, initial);
    }
  }, [activeNutrient, featuresSpecs]);

  const handleInputChange = (feature, val) => {
    const min = ranges[feature]?.min || 0;
    const max = ranges[feature]?.max || 100;
    const num = Math.min(Math.max(Number(val) || min, min), max);
    
    const updated = { ...inputValues, [feature]: num };
    setInputValues(updated);
    runPrediction(activeNutrient, updated);
  };

  const applyPreset = (mode) => {
    const updated = {};
    featuresList.forEach(feat => {
      const min = ranges[feat]?.min || 0;
      const max = ranges[feat]?.max || 100;
      if (mode === 'optimal') updated[feat] = Number(((min + max) / 2).toFixed(2));
      else if (mode === 'low') updated[feat] = Number((min + (max - min) * 0.15).toFixed(2));
      else if (mode === 'high') updated[feat] = Number((min + (max - min) * 0.85).toFixed(2));
    });
    setInputValues(updated);
    runPrediction(activeNutrient, updated);
  };

  const runPrediction = async (nutrient, inputs) => {
    setIsCalculating(true);
    const result = await predictWaterUptake(nutrient, inputs);
    setPrediction(result);
    setIsCalculating(false);
  };

  return (
    <section id="calculator-section">
      {/* Nutrient System Selector Tabs */}
      <div className="lighter-green-subheading">SELECT NUTRIENT SYSTEM</div>
      <div className="tabs-header">
        {['K', 'Mg', 'N'].map((nut) => (
          <button
            key={nut}
            className={`tab-button ${activeNutrient === nut ? 'active' : ''}`}
            onClick={() => setActiveNutrient(nut)}
          >
            {nut === 'K' && 'POTASSIUM (K) SYSTEM'}
            {nut === 'Mg' && 'MAGNESIUM (Mg) SYSTEM'}
            {nut === 'N' && 'NITROGEN (N) SYSTEM'}
          </button>
        ))}
      </div>

      {/* Warm Cream Section matching Screenshot Layout */}
      <div className="cream-panel">
        <div className="cream-split-layout">
          
          {/* Left Column: WHO WE ARE? & Sustainability Approach */}
          <div className="cream-left-column">
            <div className="lighter-green-subheading">WHO WE ARE?</div>
            <h2 className="cream-main-title">
              Know About Our<br />Sustainability Approach
            </h2>
            <p className="cream-description">
              We are a leading sustainable agronomic intelligence platform dedicated to optimizing hydroponic nutrient solutions and maximizing crop water efficiency.
            </p>

            {/* Presets Bar */}
            <div className="presets-bar" style={{ marginTop: '1.25rem' }}>
              <span className="preset-label">PRESET SCENARIOS:</span>
              <button className="preset-button" onClick={() => applyPreset('optimal')}>Optimal Growth</button>
              <button className="preset-button" onClick={() => applyPreset('low')}>Low Stress</button>
              <button className="preset-button" onClick={() => applyPreset('high')}>High Stress</button>
            </div>
          </div>

          {/* Right Column: Mission & Vision Timeline (Target & Eye Circular Badges) */}
          <div className="cream-right-column">
            
            {/* Timeline Item 1: Mission */}
            <div className="timeline-item">
              <div className="timeline-icon-badge">
                <Target size={20} color="#ffffff" />
              </div>
              <div className="timeline-content">
                <div className="lighter-green-subheading">OUR MISSION</div>
                <h3 className="timeline-title">Sustainable Hydroponics for a Better Yield</h3>
                <p className="timeline-text">
                  Our mission is to predict and minimize water waste through precise ML modeling of macro and micro nutrient ionic ratios.
                </p>
              </div>
            </div>

            {/* Timeline Vertical Connector */}
            <div className="timeline-connector-line"></div>

            {/* Timeline Item 2: Vision */}
            <div className="timeline-item">
              <div className="timeline-icon-badge">
                <Eye size={20} color="#ffffff" />
              </div>
              <div className="timeline-content">
                <div className="lighter-green-subheading">OUR VISION</div>
                <h3 className="timeline-title">A Greener, Data-Driven Tomorrow</h3>
                <p className="timeline-text">
                  Our vision is an automated hydroponic ecosystem where nutrient dosing continuously adapts to real-time soybean physiological demands.
                </p>
              </div>
            </div>

          </div>
        </div>

        {/* Dynamic Chemical Concentration Sliders */}
        <div className="header-line" style={{ margin: '2rem 0 1.5rem 0' }}></div>
        <div className="lighter-green-subheading">HYDROPONIC INPUT CONCENTRATIONS ({activeNutrient} MODEL)</div>

        <div className="inputs-grid">
          {featuresList.map((feat) => {
            const min = ranges[feat]?.min || 0;
            const max = ranges[feat]?.max || 100;
            const currentVal = inputValues[feat] !== undefined ? inputValues[feat] : ((min + max) / 2);
            const tooltip = COMPOUND_DESCRIPTIONS[feat] || feat;

            return (
              <div key={feat} className="input-control-group">
                <div className="input-label-row">
                  <span className="input-label-title">{feat}</span>
                  <span className="input-label-range">Range: {min.toFixed(2)} - {max.toFixed(2)}</span>
                </div>
                
                <div className="slider-input-row">
                  <input
                    type="range"
                    min={min}
                    max={max}
                    step={(max - min) / 100}
                    value={currentVal}
                    onChange={(e) => handleInputChange(feat, e.target.value)}
                    className="custom-range-slider"
                  />
                  <input
                    type="number"
                    min={min}
                    max={max}
                    step="0.01"
                    value={currentVal}
                    onChange={(e) => handleInputChange(feat, e.target.value)}
                    className="numeric-input-box"
                  />
                </div>
                <div className="compound-tooltip">{tooltip}</div>
              </div>
            );
          })}
        </div>

        {/* Right-Aligned Re-run Pipeline Analysis Button Container */}
        <div className="rerun-action-container">
          <button
            className="rerun-btn"
            onClick={() => runPrediction(activeNutrient, inputValues)}
          >
            <Play size={16} fill="currentColor" />
            RE-RUN PIPELINE ANALYSIS
          </button>
        </div>

      </div>

      {/* Solid Dark Prediction Output Box */}
      <div className="dark-panel">
        <div className="lighter-green-subheading">WATER UPTAKE PREDICTION OUTPUT ({activeNutrient})</div>

        <div className="output-grid">
          <div className="output-value-box">
            <div>
              <span className="output-number">
                {isCalculating ? '...' : (prediction !== null ? prediction.toFixed(2) : '--')}
              </span>
              <span className="output-unit">mL</span>
            </div>
            <div className="output-caption">Predicted Daily Soybean Water Consumption</div>
          </div>

          <div className="metric-card">
            <div className="metric-value">SVR</div>
            <div className="metric-label">Production Model</div>
          </div>

          <div className="metric-card">
            <div className="metric-value">
              {prediction > 50 ? 'OPTIMAL' : 'MODERATE'}
            </div>
            <div className="metric-label">Uptake Status</div>
          </div>
        </div>
      </div>
    </section>
  );
}
