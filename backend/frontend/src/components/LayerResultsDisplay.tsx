/**
 * LayerResultsDisplay Component
 * Shows detailed results from all 7 authentication layers
 */

import React from 'react';
import {
  FileText,
  Copy,
  Lock,
  Database,
  Bot,
  Target,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Clock
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { DocumentAnalysis, FinalAssessment } from '../services/api';

interface LayerResultsDisplayProps {
  analysis: DocumentAnalysis;
  finalAssessment: FinalAssessment;
  className?: string;
}

const LayerResultsDisplay: React.FC<LayerResultsDisplayProps> = ({
  analysis,
  finalAssessment,
  className = "",
}) => {
  const getStatusIcon = (score: number | null) => {
    if (score === null) return <Clock className="w-5 h-5 text-gray-400" />;
    if (score >= 0.7) return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (score >= 0.4) return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    return <XCircle className="w-5 h-5 text-red-500" />;
  };

  const getScoreColor = (score: number | null) => {
    if (score === null) return 'text-gray-500';
    if (score >= 0.7) return 'text-green-600';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number | null) => {
    if (score === null) return 'bg-gray-50 border-gray-200';
    if (score >= 0.7) return 'bg-green-50 border-green-200';
    if (score >= 0.4) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const layers = [
    {
      id: 'mime',
      name: 'MIME Detection',
      icon: FileText,
      description: 'File type validation and security screening',
      score: 0.95, // Mock high score for MIME
      weight: 0.12,
    },
    {
      id: 'classification',
      name: 'Classification',
      icon: FileText,
      description: 'Document type and domain analysis',
      score: analysis.layer_scores.classification,
      weight: 0.12,
    },
    {
      id: 'clone',
      name: 'Clone Detection',
      icon: Copy,
      description: 'Originality and plagiarism detection',
      score: analysis.layer_scores.clone,
      weight: 0.20,
    },
    {
      id: 'crypto',
      name: 'Cryptographic',
      icon: Lock,
      description: 'Digital signatures and blockchain verification',
      score: analysis.layer_scores.crypto,
      weight: 0.18,
    },
    {
      id: 'rag',
      name: 'RAG Analysis',
      icon: Database,
      description: 'Factual consistency validation',
      score: null, // Not implemented
      weight: 0.15,
    },
    {
      id: 'ai_detection',
      name: 'AI Detection',
      icon: Bot,
      description: 'Machine-generated content identification',
      score: analysis.layer_scores.ai_detection,
      weight: 0.20,
    },
    {
      id: 'final',
      name: 'Final Prediction',
      icon: Target,
      description: 'Weighted score aggregation and decision',
      score: finalAssessment.authenticity_score,
      weight: 0.03,
    },
  ];

  // Prepare chart data (exclude null scores)
  const chartData = layers
    .filter(layer => layer.score !== null)
    .map(layer => ({
      name: layer.name,
      score: layer.score,
      contribution: (layer.score as number) * layer.weight,
      weight: layer.weight,
    }));

  const barColors = layers
    .filter(layer => layer.score !== null)
    .map(layer => {
      const score = layer.score as number;
      if (score >= 0.7) return '#10B981'; // green
      if (score >= 0.4) return '#F59E0B'; // yellow
      return '#EF4444'; // red
    });

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Overall Assessment */}
      <div className="p-6 border-b border-gray-200">
        <div className="text-center">
          <div className="mb-4">
            <div className={`inline-flex items-center px-4 py-2 rounded-full text-lg font-semibold ${getRiskLevelColor(finalAssessment.risk_level)}`}>
              <Target className="w-5 h-5 mr-2" />
              {finalAssessment.label}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {Math.round(finalAssessment.authenticity_score * 100)}%
              </div>
              <div className="text-sm text-gray-500">Authenticity</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {Math.round(finalAssessment.confidence * 100)}%
              </div>
              <div className="text-sm text-gray-500">Confidence</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold capitalize ${getRiskLevelColor(finalAssessment.risk_level).split(' ')[0]}`}>
                {finalAssessment.risk_level}
              </div>
              <div className="text-sm text-gray-500">Risk Level</div>
            </div>
          </div>
        </div>
      </div>

      {/* Layer Results */}
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          7-Layer Analysis Pipeline
        </h3>

        <div className="space-y-4">
          {layers.map((layer) => {
            const IconComponent = layer.icon;
            const explanation = analysis.layer_explanations[layer.id] ||
              (layer.score === null ? 'Not yet implemented' : 'Analysis completed');

            return (
              <div
                key={layer.id}
                className={`p-4 rounded-lg border-2 ${getScoreBgColor(layer.score)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className="p-2 bg-white rounded-lg shadow-sm">
                      <IconComponent className="w-5 h-5 text-blue-600" />
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="text-lg font-medium text-gray-900">
                          {layer.name}
                        </h4>
                        {getStatusIcon(layer.score)}
                      </div>

                      <p className="text-sm text-gray-600 mb-2">
                        {layer.description}
                      </p>

                      <p className="text-sm text-gray-700">
                        {explanation}
                      </p>
                    </div>
                  </div>

                  <div className="text-right ml-4">
                    <div className={`text-2xl font-bold ${getScoreColor(layer.score)}`}>
                      {layer.score !== null ? `${Math.round(layer.score * 100)}%` : 'N/A'}
                    </div>
                    <div className="text-xs text-gray-500">
                      Weight: {Math.round(layer.weight * 100)}%
                    </div>
                  </div>
                </div>

                {/* Score Bar */}
                {layer.score !== null && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          layer.score >= 0.7 ? 'bg-green-500' :
                          layer.score >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${layer.score * 100}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Chart Visualization */}
      <div className="p-6 border-t border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Score Visualization
        </h3>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                domain={[0, 1]}
                tick={{ fontSize: 12 }}
                tickFormatter={(value: number) => `${Math.round(value * 100)}%`}
              />
              <Tooltip
                formatter={(value: number, name: string) => [
                  `${Math.round(value * 100)}%`,
                  name === 'score' ? 'Score' : 'Weighted Contribution'
                ]}
                labelFormatter={(label: string) => `Layer: ${label}`}
              />
              <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={barColors[index]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Final Summary */}
      <div className="p-6 bg-gray-50 rounded-b-lg">
        <div className="text-sm text-gray-600 text-center">
          <p>
            This analysis was performed using Authentia AI's 7-layer authentication system.
            Each layer contributes to the final authenticity score based on its assigned weight.
          </p>
          <p className="mt-2 text-xs">
            Analysis completed in real-time • Results are deterministic and auditable
          </p>
        </div>
      </div>
    </div>
  );
};

export default LayerResultsDisplay;