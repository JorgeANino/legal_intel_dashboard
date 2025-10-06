import { Inter } from 'next/font/google';

import './globals.css';
import { ClientProviders } from '@/providers/ClientProviders';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Legal Intelligence Dashboard',
  description: 'AI-powered legal document analysis and management',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  );
}

