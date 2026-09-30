import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import NutrientCalculator from './components/NutrientCalculator';
import DapGrowthCurve from './components/DapGrowthCurve';
import CorrelationHeatmap from './components/CorrelationHeatmap';
import FeatureDependenceCurve from './components/FeatureDependenceCurve';
import ShapSection from './components/ShapSection';
import ModelBenchmarks from './components/ModelBenchmarks';
import FooterStats from './components/FooterStats';
import {
  fetchHealth,
  fetchFeatures,
  fetchResults,
  fetchShap,
  FALLBACK_FEATURES,
  FALLBACK_RESULTS,
  FALLBACK_SHAP
} from './services/api';

export default function App() {
  const [isOnline, setIsOnline] = useState(false);
  const [featuresSpecs, setFeaturesSpecs] = useState(FALLBACK_FEATURES);
  const [resultsData, setResultsData] = useState(FALLBACK_RESULTS);
  const [shapData, setShapData] = useState(FALLBACK_SHAP);

  useEffect(() => {
    async function initData() {
      const online = await fetchHealth();
      setIsOnline(online);

      const feats = await fetchFeatures();
      setFeaturesSpecs(feats);

      const res = await fetchResults();
      setResultsData(res);

      const sh = await fetchShap();
      setShapData(sh);
    }
    initData();
  }, []);

  return (
    <div className="container">
      <Header />
      <NutrientCalculator featuresSpecs={featuresSpecs} />

      {/* 4 Scientific Graphs from Nature Article */}
      <DapGrowthCurve />
      <CorrelationHeatmap />
      <FeatureDependenceCurve />
      <ShapSection shapData={shapData} />
      <ModelBenchmarks resultsData={resultsData} />

      <FooterStats />
    </div>
  );
}
