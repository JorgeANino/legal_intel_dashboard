'use client';

import { useState } from 'react';

import { QueryFilters as QueryFiltersType } from '@/api/types';

interface Props {
  onFilterChange: (filters: QueryFiltersType) => void;
  availableFilters: {
    agreement_types: string[];
    jurisdictions: string[];
    industries: string[];
    geographies: string[];
  };
  currentFilters?: QueryFiltersType;
}

export const QueryFilters = ({
  onFilterChange,
  availableFilters,
  currentFilters,
}: Props) => {
  const [filters, setFilters] = useState<QueryFiltersType>(
    currentFilters || {},
  );

  const handleFilterChange = (
    field: keyof QueryFiltersType,
    value: string[],
  ) => {
    const newFilters = {
      ...filters,
      [field]: value.length > 0 ? value : undefined,
    };
    setFilters(newFilters);
  };

  const clearFilters = () => {
    const clearedFilters: QueryFiltersType = {};
    setFilters(clearedFilters);
    onFilterChange(clearedFilters);
  };

  const applyFilters = () => {
    onFilterChange(filters);
  };

  const hasActiveFilters = Object.values(filters).some((value) =>
    Array.isArray(value) ? value.length > 0 : value !== undefined,
  );

  return (
    <div className='bg-white p-4 border border-gray-200 rounded-lg'>
      <div className='flex items-center justify-between mb-4'>
        <h3 className='text-lg font-medium text-gray-900'>Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className='text-sm text-gray-600 hover:text-gray-800 underline'
          >
            Clear all filters
          </button>
        )}
      </div>

      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
        {/* Agreement Type Filter */}
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Agreement Type
          </label>
          <select
            multiple
            size={4}
            className='w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            onChange={(e) => {
              const selected = Array.from(
                e.target.selectedOptions,
                (option) => option.value,
              );
              handleFilterChange('agreement_types', selected);
            }}
            value={filters.agreement_types || []}
          >
            {availableFilters.agreement_types.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
          <p className='text-xs text-gray-500 mt-1'>
            Hold Ctrl/Cmd to select multiple
          </p>
        </div>

        {/* Jurisdiction Filter */}
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Jurisdiction
          </label>
          <select
            multiple
            size={4}
            className='w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            onChange={(e) => {
              const selected = Array.from(
                e.target.selectedOptions,
                (option) => option.value,
              );
              handleFilterChange('jurisdictions', selected);
            }}
            value={filters.jurisdictions || []}
          >
            {availableFilters.jurisdictions.map((jurisdiction) => (
              <option key={jurisdiction} value={jurisdiction}>
                {jurisdiction}
              </option>
            ))}
          </select>
          <p className='text-xs text-gray-500 mt-1'>
            Hold Ctrl/Cmd to select multiple
          </p>
        </div>

        {/* Industry Filter */}
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Industry
          </label>
          <select
            multiple
            size={4}
            className='w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            onChange={(e) => {
              const selected = Array.from(
                e.target.selectedOptions,
                (option) => option.value,
              );
              handleFilterChange('industries', selected);
            }}
            value={filters.industries || []}
          >
            {availableFilters.industries.map((industry) => (
              <option key={industry} value={industry}>
                {industry}
              </option>
            ))}
          </select>
          <p className='text-xs text-gray-500 mt-1'>
            Hold Ctrl/Cmd to select multiple
          </p>
        </div>

        {/* Geography Filter */}
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-2'>
            Geography
          </label>
          <select
            multiple
            size={4}
            className='w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            onChange={(e) => {
              const selected = Array.from(
                e.target.selectedOptions,
                (option) => option.value,
              );
              handleFilterChange('geographies', selected);
            }}
            value={filters.geographies || []}
          >
            {availableFilters.geographies.map((geography) => (
              <option key={geography} value={geography}>
                {geography}
              </option>
            ))}
          </select>
          <p className='text-xs text-gray-500 mt-1'>
            Hold Ctrl/Cmd to select multiple
          </p>
        </div>
      </div>

      <div className='mt-4 flex justify-end'>
        <button
          onClick={applyFilters}
          className='px-4 py-2 text-sm bg-primary text-white rounded-md hover:bg-primary-dark transition-colors'
        >
          Apply Filters
        </button>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className='mt-4 pt-4 border-t border-gray-200'>
          <h4 className='text-sm font-medium text-gray-700 mb-2'>
            Active Filters:
          </h4>
          <div className='flex flex-wrap gap-2'>
            {filters.agreement_types?.map((type) => (
              <span
                key={type}
                className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800'
              >
                Agreement: {type}
              </span>
            ))}
            {filters.jurisdictions?.map((jurisdiction) => (
              <span
                key={jurisdiction}
                className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800'
              >
                Jurisdiction: {jurisdiction}
              </span>
            ))}
            {filters.industries?.map((industry) => (
              <span
                key={industry}
                className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800'
              >
                Industry: {industry}
              </span>
            ))}
            {filters.geographies?.map((geography) => (
              <span
                key={geography}
                className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800'
              >
                Geography: {geography}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
