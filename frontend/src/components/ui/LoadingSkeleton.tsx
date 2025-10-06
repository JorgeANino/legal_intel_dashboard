export const LoadingSkeleton = ({ className = '' }: { className?: string }) => {
  return (
    <div className={`animate-pulse ${className}`}>
      <div className='h-4 bg-gray-200 rounded w-3/4'></div>
      <div className='h-4 bg-gray-200 rounded w-1/2 mt-2'></div>
    </div>
  );
};

export const CardSkeleton = () => {
  return (
    <div className='bg-white p-6 rounded-lg shadow-sm border border-gray-200 animate-pulse'>
      <div className='h-4 bg-gray-200 rounded w-1/4'></div>
      <div className='h-8 bg-gray-200 rounded w-1/2 mt-4'></div>
      <div className='h-3 bg-gray-200 rounded w-1/3 mt-2'></div>
    </div>
  );
};

export const TableSkeleton = () => {
  return (
    <div className='space-y-3 animate-pulse'>
      {[...Array(5)].map((_, i) => (
        <div key={i} className='h-12 bg-gray-200 rounded'></div>
      ))}
    </div>
  );
};
