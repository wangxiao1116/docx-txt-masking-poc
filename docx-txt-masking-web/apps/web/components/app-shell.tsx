import { Activity, Database, FileText, ShieldCheck, UploadCloud } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      <aside className="w-64 shrink-0 bg-sidebar text-slate-100">
        <div className="border-b border-white/10 px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-blue-500">
              <ShieldCheck className="h-5 w-5" aria-hidden />
            </div>
            <div>
              <div className="text-sm font-semibold">脱敏验证工作台</div>
              <div className="text-xs text-slate-300">客户验证版</div>
            </div>
          </div>
        </div>
        <nav className="space-y-1 px-3 py-4 text-sm">
          {([
            [UploadCloud, "文件上传"],
            [FileText, "处理清单"],
            [Database, "导出结果"],
            [Activity, "复检状态"],
          ] as Array<[LucideIcon, string]>).map(([Icon, label]) => (
            <div key={label} className="flex items-center gap-3 rounded-md px-3 py-2 text-slate-200">
              <Icon className="h-4 w-4" aria-hidden />
              <span>{label}</span>
            </div>
          ))}
        </nav>
      </aside>
      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
