'use client';

import { useState, FormEvent } from 'react';
import { useDocumentQuery } from '@/hooks/useDocumentQuery';

const EXAMPLE_QUERIES = [
  'Which agreements are governed by UAE law?',
  'Show me all NDAs',
  'List all technology contracts',
  'Find agreements in the oil & gas industry',
  'What contracts are from the Middle East?',
];

export const QueryInput = () => {
  const [question, setQuestion] = useState('');
  const { executeQuery, isQuerying } = useDocumentQuery();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (question.trim()) {
      executeQuery({ question: question.trim(), max_results: 50 });
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your documents..."
            disabled={isQuerying}
            className="w-full px-4 py-3 pr-24 border border-gray-300 rounded-lg 
                     focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isQuerying || !question.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2
                     px-6 py-2 bg-primary text-white rounded-md
                     hover:bg-primary-dark transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isQuerying ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Searching...
              </span>
            ) : (
              'Search'
            )}
          </button>
        </div>

        {/* Character count */}
        <div className="flex justify-between items-center text-sm text-gray-500">
          <span>{question.length} characters</span>
          <span className="text-xs">Tip: Be specific for better results</span>
        </div>
      </form>

      {/* Example Questions */}
      <div>
        <p className="text-sm font-medium text-gray-700 mb-2">Example questions:</p>
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_QUERIES.map((example, idx) => (
            <button
              key={idx}
              onClick={() => setQuestion(example)}
              disabled={isQuerying}
              className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 
                       rounded-full transition-colors disabled:opacity-50"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

