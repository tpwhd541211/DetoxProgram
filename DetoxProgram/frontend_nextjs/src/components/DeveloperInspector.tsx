import React, { useState, useRef } from "react";
import { Bug, X, Copy, Check, TerminalSquare } from "lucide-react";

interface DeveloperInspectorProps {
  state: {
    step?: string;
    datasetId?: string | null;
    scores?: any;
    report?: any;
    personaData?: any;
    graphData?: any;
    realtimeData?: any;
    guideData?: any;
    contents?: any;
  };
}

export default function DeveloperInspector({ state }: DeveloperInspectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("graphData");
  const [copied, setCopied] = useState(false);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 p-3 bg-slate-800 text-green-400 rounded-full shadow-2xl hover:bg-slate-700 hover:scale-110 transition-all z-[9999] border border-slate-600 flex items-center gap-2 group"
        title="Developer Inspector"
      >
        <Bug size={24} />
        <span className="w-0 overflow-hidden opacity-0 group-hover:w-auto group-hover:opacity-100 transition-all whitespace-nowrap text-xs font-mono font-bold">
          DEV INSPECTOR
        </span>
      </button>
    );
  }

  const tabs = Object.keys(state).filter(k => state[k as keyof typeof state] !== undefined);
  const currentData = state[activeTab as keyof typeof state];

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(currentData, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed bottom-6 right-6 w-[600px] h-[700px] max-h-[85vh] max-w-[90vw] bg-[#0f172a] rounded-xl shadow-2xl z-[9999] border border-slate-700 flex flex-col font-mono overflow-hidden text-slate-300">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#1e293b] border-b border-slate-700">
        <div className="flex items-center gap-2 text-green-400 font-bold">
          <TerminalSquare size={18} />
          <span>DEVELOPER INSPECTOR</span>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-slate-400 hover:text-white transition-colors p-1"
        >
          <X size={20} />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex overflow-x-auto bg-[#0f172a] border-b border-slate-800 scrollbar-hide">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-xs font-semibold whitespace-nowrap transition-colors border-b-2 ${
              activeTab === tab
                ? "border-green-400 text-green-400 bg-slate-800"
                : "border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-800/50"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#1e293b]/50 border-b border-slate-800">
        <span className="text-xs text-slate-500">
          Data Type: <span className="text-blue-300">{typeof currentData}</span>
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors bg-slate-800 px-2 py-1 rounded"
        >
          {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
          {copied ? "Copied!" : "Copy JSON"}
        </button>
      </div>

      {/* JSON Viewer */}
      <div className="flex-1 overflow-auto p-4 bg-[#09090b]">
        {currentData === undefined || currentData === null ? (
          <span className="text-slate-500 italic">null or undefined</span>
        ) : (
          <pre className="text-[11px] leading-relaxed text-blue-200">
            {JSON.stringify(currentData, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
