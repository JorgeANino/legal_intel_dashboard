'use client';

import { DashboardStats } from '@/api/types';

interface Props {
  stats: DashboardStats;
}

export const StatsCards = ({ stats }: Props) => {
  const cards = [
    {
      title: 'Total Documents',
      value: stats.total_documents,
      subtitle: `${stats.processed_documents} processed`,
      icon: (
        <svg
          className='w-8 h-8'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
          />
        </svg>
      ),
      color: 'blue',
    },
    {
      title: 'Total Pages',
      value: stats.total_pages.toLocaleString(),
      subtitle: 'Analyzed',
      icon: (
        <svg
          className='w-8 h-8'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z'
          />
        </svg>
      ),
      color: 'green',
    },
    {
      title: 'Agreement Types',
      value: Object.keys(stats.agreement_types).length,
      subtitle: 'Different types',
      icon: (
        <svg
          className='w-8 h-8'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2'
          />
        </svg>
      ),
      color: 'purple',
    },
    {
      title: 'Jurisdictions',
      value: Object.keys(stats.jurisdictions).length,
      subtitle: 'Covered',
      icon: (
        <svg
          className='w-8 h-8'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
          />
        </svg>
      ),
      color: 'orange',
    },
  ];

  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    purple: 'text-purple-600 bg-purple-100',
    orange: 'text-orange-600 bg-orange-100',
  };

  return (
    <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
      {cards.map((card, idx) => (
        <div
          key={idx}
          className='bg-white rounded-lg shadow-sm border border-gray-200 p-6
                   hover:shadow-md transition-shadow'
        >
          <div className='flex items-center justify-between'>
            <div>
              <p className='text-sm font-medium text-gray-600'>{card.title}</p>
              <p className='text-3xl font-bold text-gray-900 mt-2'>
                {card.value}
              </p>
              <p className='text-xs text-gray-500 mt-1'>{card.subtitle}</p>
            </div>
            <div
              className={`p-3 rounded-full ${colorClasses[card.color as keyof typeof colorClasses]}`}
            >
              {card.icon}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
