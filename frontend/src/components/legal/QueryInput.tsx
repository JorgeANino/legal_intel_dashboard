'use client';

import { useState, FormEvent, useEffect, useRef } from 'react';

import { useDebounce } from '@/hooks/useDebounce';
import { useDocumentQuery } from '@/hooks/useDocumentQuery';
import { useQuerySuggestions } from '@/hooks/useQuerySuggestions';

const EXAMPLE_QUERIES = [
  'Which agreements are governed by UAE law?',
  'Show me all NDAs',
  'List all technology contracts',
  'Find agreements in the oil & gas industry',
  'What contracts are from the Middle East?',
];

export const QueryInput = () => {
  const [question, setQuestion] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  const { executeQuery, isQuerying } = useDocumentQuery();
  const {
    suggestions,
    isLoading: suggestionsLoading,
    fetchSuggestions,
    clearSuggestions,
  } = useQuerySuggestions();
  const debouncedQuery = useDebounce(question, 300);

  // Fetch suggestions when query changes
  useEffect(() => {
    if (debouncedQuery.length > 2) {
      fetchSuggestions(debouncedQuery);
      setShowSuggestions(true);
    } else {
      clearSuggestions();
      setShowSuggestions(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery]);

  // Handle clicking outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (question.trim()) {
      executeQuery(question.trim());
      setShowSuggestions(false);
    }
  };

  const selectSuggestion = (suggestion: string) => {
    setQuestion(suggestion);
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
    executeQuery(suggestion);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedSuggestionIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev,
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedSuggestionIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedSuggestionIndex >= 0) {
          selectSuggestion(suggestions[selectedSuggestionIndex]);
        } else {
          handleSubmit(e);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedSuggestionIndex(-1);
        break;
    }
  };

  return (
    <div className='space-y-6'>
      <form onSubmit={handleSubmit} className='space-y-4'>
        <div className='relative'>
          <input
            ref={inputRef}
            type='text'
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(question.length > 2)}
            placeholder='Ask a question about your documents...'
            disabled={isQuerying}
            className='w-full px-4 py-3 pr-24 border border-gray-300 rounded-lg 
                     focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed'
          />

          {/* Suggestions Dropdown */}
          {showSuggestions &&
            (suggestions.length > 0 || suggestionsLoading) && (
              <div
                ref={suggestionsRef}
                className='absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto'
              >
                {suggestionsLoading ? (
                  <div className='px-4 py-2 text-sm text-gray-500 flex items-center'>
                    <svg
                      className='animate-spin -ml-1 mr-2 h-4 w-4'
                      fill='none'
                      viewBox='0 0 24 24'
                    >
                      <circle
                        className='opacity-25'
                        cx='12'
                        cy='12'
                        r='10'
                        stroke='currentColor'
                        strokeWidth='4'
                      />
                      <path
                        className='opacity-75'
                        fill='currentColor'
                        d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
                      />
                    </svg>
                    Loading suggestions...
                  </div>
                ) : (
                  suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className={`px-4 py-2 text-sm cursor-pointer transition-colors ${
                        index === selectedSuggestionIndex
                          ? 'bg-primary text-white'
                          : 'hover:bg-gray-100'
                      }`}
                      onClick={() => selectSuggestion(suggestion)}
                      onMouseEnter={() => setSelectedSuggestionIndex(index)}
                    >
                      {suggestion}
                    </div>
                  ))
                )}
              </div>
            )}
          <button
            type='submit'
            disabled={isQuerying || !question.trim()}
            className='absolute right-2 top-1/2 -translate-y-1/2
                     px-6 py-2 bg-primary text-white rounded-md
                     hover:bg-primary-dark transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed'
          >
            {isQuerying ? (
              <span className='flex items-center'>
                <svg
                  className='animate-spin -ml-1 mr-2 h-4 w-4'
                  fill='none'
                  viewBox='0 0 24 24'
                >
                  <circle
                    className='opacity-25'
                    cx='12'
                    cy='12'
                    r='10'
                    stroke='currentColor'
                    strokeWidth='4'
                  />
                  <path
                    className='opacity-75'
                    fill='currentColor'
                    d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
                  />
                </svg>
                Searching...
              </span>
            ) : (
              'Search'
            )}
          </button>
        </div>

        {/* Character count */}
        <div className='flex justify-between items-center text-sm text-gray-500'>
          <span>{question.length} characters</span>
          <span className='text-xs'>Tip: Be specific for better results</span>
        </div>
      </form>

      {/* Example Questions */}
      <div>
        <p className='text-sm font-medium text-gray-700 mb-2'>
          Example questions:
        </p>
        <div className='flex flex-wrap gap-2'>
          {EXAMPLE_QUERIES.map((example, idx) => (
            <button
              key={idx}
              onClick={() => setQuestion(example)}
              disabled={isQuerying}
              className='px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 
                       rounded-full transition-colors disabled:opacity-50'
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
