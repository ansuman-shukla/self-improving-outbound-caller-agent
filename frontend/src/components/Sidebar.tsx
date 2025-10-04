"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Library, FlaskConical, PlayCircle, Home, Zap } from "lucide-react";

const navigation = [
  {
    name: "Outbound Caller Dashboard",
    href: "/",
    icon: Home,
    description: "Initiate calls & view history",
  },
  {
    name: "Library Hub",
    href: "/library",
    icon: Library,
    description: "Manage Personalities & Prompts",
  },
  {
    name: "Scenario Designer",
    href: "/scenarios",
    icon: FlaskConical,
    description: "Generate & Edit Test Scenarios",
  },
  {
    name: "Evaluation Hub",
    href: "/evaluations",
    icon: PlayCircle,
    description: "Run Tests & View Results",
  },
  {
    name: "Tuning Hub",
    href: "/tuning",
    icon: Zap,
    description: "Automated Prompt Optimization",
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div 
      className={`flex h-screen flex-col bg-card border-r border-border text-foreground transition-all duration-300 ease-in-out ${
        isExpanded ? "w-64" : "w-16"
      }`}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      {/* Logo/Title */}
      <div className="flex h-16 items-center justify-center border-b border-border px-4">
        {isExpanded ? (
          <h1 className="text-xl font-bold text-foreground whitespace-nowrap">Voice Agent Evaluator</h1>
        ) : (
          <span className="text-xl font-bold text-foreground">VA</span>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname?.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                group flex flex-col rounded-lg px-3 py-3 text-sm font-medium transition-colors
                ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }
              `}
              title={!isExpanded ? item.name : ""}
            >
              <div className="flex items-center gap-3">
                <Icon className="h-5 w-5 flex-shrink-0" />
                {isExpanded && <span className="whitespace-nowrap">{item.name}</span>}
              </div>
              {isExpanded && (
                <span className={`ml-8 mt-1 text-xs ${isActive ? "text-primary-foreground/70" : "text-muted-foreground"}`}>
                  {item.description}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {isExpanded && (
        <div className="border-t border-border p-4">
          <p className="text-center text-xs text-muted-foreground">
            Voice Agent Platform v1.0
          </p>
        </div>
      )}
    </div>
  );
}
