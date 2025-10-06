'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

import { useAuth } from '@/hooks/useAuth';

export default function Navigation() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: '/' },
    { name: 'Upload', href: '/upload' },
    { name: 'Query', href: '/query' },
  ];

  return (
    <nav className='bg-white shadow-sm border-b border-gray-200'>
      <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
        <div className='flex justify-between h-16'>
          <div className='flex'>
            <div className='flex-shrink-0 flex items-center'>
              <div className='w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-md'>
                <svg
                  className='w-6 h-6 text-white'
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
              </div>
              <span className='ml-3 text-xl font-bold text-gray-900'>
                Legal Intel
              </span>
            </div>
            <div className='hidden sm:ml-8 sm:flex sm:space-x-8'>
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                      isActive
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                  >
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
          <div className='flex items-center'>
            {user && (
              <div className='flex items-center space-x-4'>
                <div className='text-sm'>
                  <div className='font-medium text-gray-700'>
                    {user.full_name}
                  </div>
                  <div className='text-gray-500'>{user.email}</div>
                </div>
                <button
                  onClick={logout}
                  className='inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors'
                >
                  <svg
                    className='mr-2 h-4 w-4'
                    fill='none'
                    stroke='currentColor'
                    viewBox='0 0 24 24'
                  >
                    <path
                      strokeLinecap='round'
                      strokeLinejoin='round'
                      strokeWidth={2}
                      d='M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1'
                    />
                  </svg>
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
