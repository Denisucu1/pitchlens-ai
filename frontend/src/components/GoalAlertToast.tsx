import React, { useState, useEffect } from "react";
import type { GoalAlert } from "../types";
import { Bell, X } from "lucide-react";

interface GoalAlertToastProps {
  alert: GoalAlert | null | undefined;
}

export const GoalAlertToast: React.FC<GoalAlertToastProps> = ({ alert }) => {
  const [visible, setVisible] = useState(false);
  const [currentAlert, setCurrentAlert] = useState<GoalAlert | null>(null);

  useEffect(() => {
    if (alert && alert.alert_id !== currentAlert?.alert_id) {
      setCurrentAlert(alert);
      setVisible(true);

      const timer = setTimeout(() => {
        setVisible(false);
      }, 7000);

      return () => clearTimeout(timer);
    }
  }, [alert]);

  if (!visible || !currentAlert) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-sm animate-in slide-in-from-bottom-5 duration-300">
      <div className="bg-gradient-to-r from-[#1b0826] via-[#2d093f] to-[#12031a] border-2 border-[#00FF87] rounded-2xl p-3.5 shadow-[0_0_30px_rgba(0,255,135,0.35)] text-white flex items-start gap-3 backdrop-blur-md">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#00FF87] to-[#04F5FF] flex items-center justify-center text-black font-black flex-shrink-0 text-base shadow-md">
          ⚽
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-black text-[#00FF87] uppercase tracking-wider flex items-center gap-1">
              <Bell className="w-3 h-3 text-[#00FF87] animate-bounce" />
              PREMIER LEAGUE GOAL ALERT
            </span>
            <button
              onClick={() => setVisible(false)}
              className="text-gray-400 hover:text-white p-0.5 rounded transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <h5 className="font-extrabold text-sm text-yellow-300 mt-0.5 leading-snug">
            {currentAlert.home_name} {currentAlert.score_home} - {currentAlert.score_away} {currentAlert.away_name}
          </h5>

          <p className="text-xs text-gray-200 mt-1 font-sans">
            {currentAlert.text}
          </p>
        </div>
      </div>
    </div>
  );
};
