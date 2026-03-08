import { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { ManualEntry } from './components/ManualEntry';
import { ContentIdeas } from './components/ContentIdeas';
import { LearningLog } from './components/LearningLog';
import {
  BarChart3,
  PlusCircle,
  Lightbulb,
  Brain,
} from 'lucide-react';
import './index.css';

type Tab = 'dashboard' | 'add' | 'ideas' | 'learning';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 size={20} /> },
    { id: 'add', label: 'Add Data', icon: <PlusCircle size={20} /> },
    { id: 'ideas', label: 'Content Ideas', icon: <Lightbulb size={20} /> },
    { id: 'learning', label: 'Insights', icon: <Brain size={20} /> },
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold bg-gradient-to-r from-pink-500 to-violet-500 bg-clip-text text-transparent">
            TikTok Growth Tracker
          </h1>
          <span className="text-sm text-gray-400">Tech / Programming</span>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b border-gray-800 bg-gray-900/50">
        <div className="max-w-7xl mx-auto px-4 flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                activeTab === tab.id
                  ? 'border-pink-500 text-pink-400'
                  : 'border-transparent text-gray-400 hover:text-gray-200'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'add' && <ManualEntry />}
        {activeTab === 'ideas' && <ContentIdeas />}
        {activeTab === 'learning' && <LearningLog />}
      </main>
    </div>
  );
}

export default App;
