import { cn } from "@/lib/utils";

const styles: Record<string, string> = {
  处理成功: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  处理中: "bg-blue-50 text-blue-700 ring-blue-200",
  部分成功: "bg-orange-50 text-orange-700 ring-orange-200",
  处理失败: "bg-red-50 text-red-700 ring-red-200",
  未发现敏感实体: "bg-slate-100 text-slate-700 ring-slate-200",
  通过: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  未通过: "bg-red-50 text-red-700 ring-red-200",
};

export function StatusBadge({ value }: { value: string }) {
  return (
    <span className={cn("inline-flex rounded-full px-2 py-0.5 text-xs font-medium ring-1", styles[value] ?? styles["未发现敏感实体"])}>
      {value}
    </span>
  );
}
