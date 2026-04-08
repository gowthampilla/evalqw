"use client";
import { useEffect, useState } from "react";

export default function Dashboard() {
  const [pendingActions, setPendingActions] = useState<any>({});
  const [history, setHistory] = useState<any[]>([]);

  const fetchActions = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/v1/dashboard/pending");
      const data = await res.json();
      setPendingActions(data);
    } catch (e) { console.error("API Offline"); }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/v1/dashboard/history");
      const data = await res.json();
      if (Array.isArray(data)) setHistory(data);
    } catch (e) { console.error("History fetch failed"); }
  };

  const handleApprove = async (id: string) => {
    console.log("🚀 Attempting to approve ID:", id);
    try {
      const res = await fetch(`http://127.0.0.1:8000/v1/dashboard/approve/${id}`, {
        method: "POST",
      });
      const data = await res.json();
      
      if (data.status === "ERROR" || data.status === "DB_ERROR") {
        alert(`Failed: ${data.message || data.error}`);
      } else {
        console.log("✅ Approved:", data);
        fetchActions();
        fetchHistory();
      }
    } catch (error) {
      alert("Network Error: Is FastAPI running?");
    }
  };

  const handleReject = async (id: string) => {
    await fetch(`http://127.0.0.1:8000/v1/dashboard/reject/${id}`, { method: "DELETE" });
    fetchActions();
    fetchHistory();
  };

  useEffect(() => {
    fetchActions();
    fetchHistory();
    const interval = setInterval(() => {
      fetchActions();
      fetchHistory();
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-10 font-sans">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-black italic tracking-tighter uppercase underline decoration-emerald-500">EvalsHQ Command</h1>
          <p className="text-gray-500 text-xs mt-2 font-mono uppercase tracking-widest">Human-in-the-Loop Gateway</p>
        </header>

        {/* PENDING TABLE */}
        <div className="grid gap-4 mb-20">
          {Object.keys(pendingActions).length === 0 ? (
            <div className="p-10 border border-gray-900 rounded-xl text-center text-gray-700 italic font-mono uppercase">System Clear // No Pending Actions</div>
          ) : (
            Object.entries(pendingActions).map(([id, action]: any) => (
              <div key={id} className="bg-gray-900/40 border border-gray-800 p-6 rounded-2xl flex items-center gap-6 border-l-4 border-l-emerald-500">
                <div className="w-40 shrink-0">
                  <p className="text-[10px] text-gray-600 font-mono">ID: {id.substring(0,8)}</p>
                  <p className="font-bold text-blue-400">{action.agent}</p>
                </div>
                
                <div className="flex-1">
                  <div className="flex justify-between text-[10px] uppercase font-bold mb-1">
                    <span className={action.risk_score > 70 ? 'text-red-500' : 'text-emerald-400'}>Risk: {action.risk_score}</span>
                    <span className="text-gray-600">{action.category}</span>
                  </div>
                  <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
                    <div className={`h-full ${action.risk_score > 70 ? 'bg-red-500 shadow-[0_0_10px_red]' : 'bg-emerald-500'}`} style={{ width: `${action.risk_score}%` }}></div>
                  </div>
                </div>

                <div className="flex-1">
                  <code className="text-xs text-red-400 bg-red-950/20 p-2 rounded block truncate border border-red-900/30">{action.query}</code>
                  <p className="text-[10px] mt-1 text-orange-500 font-bold italic tracking-wider">➔ {action.impact}</p>
                </div>

                <div className="flex gap-2">
                  <button onClick={() => handleReject(id)} className="px-5 py-2 bg-gray-800 text-gray-500 rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-red-950 hover:text-red-500 transition-all">Kill</button>
                  <button onClick={() => handleApprove(id)} className="px-5 py-2 bg-white text-black rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-emerald-400 hover:scale-105 transition-all active:scale-95">Approve</button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* ACTIVITY HISTORY */}
        <div>
          <h2 className="text-xs font-bold text-gray-600 uppercase tracking-[0.3em] mb-6 border-b border-gray-900 pb-2">Activity History</h2>
          <div className="space-y-2 opacity-60">
            {history.map((log: any, i) => (
              <div key={i} className="flex justify-between items-center p-3 bg-gray-900/10 border border-gray-900 rounded-lg text-[11px] font-mono">
                <div className="flex gap-4 items-center">
                  <span className={log.status === 'APPROVED' ? 'text-emerald-500 font-bold' : 'text-red-700 font-bold'}>[{log.status}]</span>
                  <span className="text-gray-500">{log.agent}:</span>
                  <span className="text-gray-400 truncate max-w-sm italic">"{log.query}"</span>
                </div>
                <span className="text-gray-400 font-bold">{log.db_result || 'REJECTED'}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}