import React from 'react';
import { Sparkles, TrendingUp, Compass, Rocket, Layers } from 'lucide-react';

interface WelcomeScreenProps {
  onSelectPrompt: (prompt: string) => void;
}

const SUGGESTED_PROMPTS = [
  {
    icon: TrendingUp,
    title: 'User Retention & Activation',
    prompt: 'How can startups improve user retention?',
    desc: 'Retention curves, onboarding friction, and core habit loops.',
  },
  {
    icon: Layers,
    title: 'Product-Led Growth (PLG)',
    prompt: 'What are the most effective product-led growth strategies?',
    desc: 'Self-serve funnels, viral loops, and freemium conversions.',
  },
  {
    icon: Compass,
    title: 'Feature Prioritization',
    prompt: 'How should a product manager prioritize features?',
    desc: 'Brian Chesky, Marty Cagan, and Shreyas Doshi frameworks.',
  },
  {
    icon: Rocket,
    title: 'Product Launch Playbook',
    prompt: 'What makes a successful product launch?',
    desc: 'Narrative design, positioning, and cross-functional momentum.',
  },
];

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSelectPrompt }) => {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-3xl mx-auto select-none">
      {/* Hero Badge */}
      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-violet-950/60 border border-violet-700/50 text-violet-300 text-xs font-medium mb-6 shadow-inner">
        <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
        <span>300+ Verified Transcripts Indexed</span>
      </div>

      {/* Hero Title */}
      <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-3">
        The Lenny Growth Assistant
      </h2>

      {/* Subtitle */}
      <p className="text-sm sm:text-base text-slate-300 max-w-xl mb-10 leading-relaxed">
        Turn the world&apos;s best product and growth conversations into actionable insights.
      </p>

      {/* Suggested Prompts Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 w-full text-left">
        {SUGGESTED_PROMPTS.map((item, index) => {
          const Icon = item.icon;
          return (
            <button
              key={index}
              onClick={() => onSelectPrompt(item.prompt)}
              className="group p-4 rounded-2xl bg-[#1E293B]/70 hover:bg-[#1E293B] border border-[#334155] hover:border-cyan-500/50 transition-all duration-200 text-left cursor-pointer hover:shadow-lg hover:shadow-cyan-500/10 active:scale-[0.99]"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-950 border border-indigo-700/40 flex items-center justify-center text-cyan-400 group-hover:text-cyan-300 group-hover:scale-105 transition-transform">
                  <Icon className="w-4 h-4" />
                </div>
                <h3 className="text-xs font-semibold text-white group-hover:text-cyan-300 transition-colors">
                  {item.title}
                </h3>
              </div>
              <p className="text-xs text-slate-300 line-clamp-2">
                &ldquo;{item.prompt}&rdquo;
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
