'use client';

import { useDashboard } from '@/hooks/useDashboard';
import { useExport } from '@/hooks/useExport';
import { StatsCards } from '@/components/legal/StatsCards';
import { AgreementTypesChart } from '@/components/legal/AgreementTypesChart';
import { JurisdictionChart } from '@/components/legal/JurisdictionChart';
import { CardSkeleton } from '@/components/ui/LoadingSkeleton';
import { ErrorDisplay } from '@/components/ui/ErrorDisplay';
import AuthGuard from '@/guards/AuthGuard';

export default function DashboardPage() {
  const { stats, isLoading, error, refetch } = useDashboard();
  const { exportDashboardReport, isExporting } = useExport();

  return (
    <AuthGuard>
      {error ? (
        <div className="p-6">
          <div className="max-w-7xl mx-auto">
            <ErrorDisplay
              title="Failed to load dashboard"
              message={error instanceof Error ? error.message : 'Unknown error'}
              onRetry={refetch}
            />
          </div>
        </div>
      ) : (
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="mt-2 text-gray-600">
                Overview of your legal document collection
              </p>
            </div>
            
            <button
              onClick={() => stats && exportDashboardReport(stats)}
              disabled={isExporting || !stats}
              className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark
                       disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isExporting ? 'Exporting...' : 'Export Report'}
            </button>
          </div>
          
          <div className="space-y-8">
          {/* Stats Cards */}
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          ) : stats ? (
            <StatsCards stats={stats} />
          ) : null}

          {/* Charts */}
          {isLoading ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 h-96 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                </div>
              ))}
            </div>
          ) : stats ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AgreementTypesChart stats={stats} />
              <JurisdictionChart stats={stats} />
            </div>
          ) : null}

          {/* Industry & Geography Tables */}
          {!isLoading && stats && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Industry Coverage</h2>
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Industry</th>
                      <th className="text-right py-2">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(stats.industries).map(([industry, count]) => (
                      <tr key={industry} className="border-b">
                        <td className="py-2">{industry}</td>
                        <td className="text-right py-2">{count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Geographic Coverage</h2>
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Geography</th>
                      <th className="text-right py-2">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(stats.geographies).map(([geography, count]) => (
                      <tr key={geography} className="border-b">
                        <td className="py-2">{geography}</td>
                        <td className="text-right py-2">{count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          </div>
        </div>
      )}
    </AuthGuard>
  );
}

