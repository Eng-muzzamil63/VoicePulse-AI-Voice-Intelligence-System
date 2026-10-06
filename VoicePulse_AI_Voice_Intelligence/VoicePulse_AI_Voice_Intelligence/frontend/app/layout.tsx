import './globals.css';

export const metadata = {
  title: 'VoicePulse AI — Conversation Intelligence',
  description: 'Deep-learning powered voice intelligence for customer operations',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
