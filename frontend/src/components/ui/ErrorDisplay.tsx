interface Props {
  title?: string;
  message?: string;
  errors?: string[];
  onDismiss?: () => void;
  onRetry?: () => void;
}

export const ErrorDisplay = ({
  title = 'Error',
  message,
  errors = [],
  onDismiss,
  onRetry,
}: Props) => {
  return (
    <div className='bg-red-50 border border-red-200 rounded-lg p-4'>
      <div className='flex items-start'>
        <svg
          className='w-5 h-5 text-red-400 mt-0.5'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
          />
        </svg>

        <div className='ml-3 flex-1'>
          <h3 className='text-sm font-medium text-red-800'>{title}</h3>
          {message && <p className='text-sm text-red-700 mt-1'>{message}</p>}

          {errors.length > 0 && (
            <ul className='list-disc list-inside text-sm text-red-700 mt-2 space-y-1'>
              {errors.map((error, idx) => (
                <li key={idx}>{error}</li>
              ))}
            </ul>
          )}

          <div className='flex gap-3 mt-4'>
            {onRetry && (
              <button
                onClick={onRetry}
                className='text-sm font-medium text-red-800 hover:text-red-900'
              >
                Try again
              </button>
            )}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className='text-sm font-medium text-red-600 hover:text-red-700'
              >
                Dismiss
              </button>
            )}
          </div>
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className='ml-auto text-red-400 hover:text-red-500'
          >
            <svg
              className='w-5 h-5'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M6 18L18 6M6 6l12 12'
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};
