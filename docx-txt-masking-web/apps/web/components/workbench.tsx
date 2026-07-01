"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  Download,
  FileArchive,
  FileDown,
  Loader2,
  RefreshCw,
  Search,
  Trash2,
  UploadCloud,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Select, Textarea } from "@/components/ui/input";
import { deleteFile, downloadUrl, listFiles, manifestUrl, uploadFile, zipUrl } from "@/lib/api";
import { formatBytes } from "@/lib/utils";
import type { FileTask } from "@/types/api";

const uploadSchema = z.object({
  file: z.custom<File>((value) => value instanceof File, "请选择 DOCX 或 TXT 文件"),
  category_code: z.string().min(1, "分类编码不能为空"),
  category_name: z.string().min(1, "分类名称不能为空"),
  level: z.string().min(1, "请选择分级标签"),
  note: z.string().optional(),
});

type UploadValues = z.infer<typeof uploadSchema>;

const steps = ["上传中", "解析文件", "提取实体", "执行遮蔽", "文件重建", "输出复检", "完成"];

export function Workbench() {
  const [tasks, setTasks] = useState<FileTask[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [stepIndex, setStepIndex] = useState(-1);
  const [message, setMessage] = useState("");
  const [search, setSearch] = useState("");
  const [fileType, setFileType] = useState("");
  const [levelFilter, setLevelFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [verificationFilter, setVerificationFilter] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const form = useForm<UploadValues>({
    resolver: zodResolver(uploadSchema),
    defaultValues: {
      category_code: "A1-1",
      category_name: "个人信息",
      level: "第3级",
      note: "",
    },
  });

  async function refresh() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (fileType) params.set("file_type", fileType);
      if (levelFilter) params.set("level", levelFilter);
      if (statusFilter) params.set("process_status", statusFilter);
      if (verificationFilter) params.set("verification_status", verificationFilter);
      const payload = await listFiles(params);
      setTasks(payload.items);
      setTotal(payload.total);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "清单加载失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function onSubmit(values: UploadValues) {
    setSubmitting(true);
    setMessage("");
    setStepIndex(0);
    const timer = window.setInterval(() => {
      setStepIndex((current) => (current >= steps.length - 2 ? current : current + 1));
    }, 320);
    try {
      const formData = new FormData();
      formData.append("file", values.file);
      formData.append("category_code", values.category_code);
      formData.append("category_name", values.category_name);
      formData.append("level", values.level);
      formData.append("note", values.note ?? "");
      const task = await uploadFile(formData);
      setStepIndex(steps.length - 1);
      setMessage(`已创建任务：${task.original_file_name}（${task.process_status}）`);
      form.reset({ category_code: "A1-1", category_name: "个人信息", level: "第3级", note: "" });
      setSelectedFile(null);
      await refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "上传处理失败");
    } finally {
      window.clearInterval(timer);
      setSubmitting(false);
      window.setTimeout(() => setStepIndex(-1), 1200);
    }
  }

  async function removeTask(id: string) {
    if (!window.confirm("确认删除该记录并同步删除本地原文与脱敏文件？")) return;
    await deleteFile(id);
    await refresh();
  }

  const columns = useMemo<ColumnDef<FileTask>[]>(
    () => [
      {
        header: "文件名",
        accessorKey: "original_file_name",
        cell: ({ row }) => (
          <div>
            <Link className="font-medium text-blue-700 hover:underline" href={`/files/${row.original.id}`}>
              {row.original.original_file_name}
            </Link>
            <div className="text-xs text-slate-500">{formatBytes(row.original.file_size)}</div>
          </div>
        ),
      },
      { header: "格式", accessorKey: "file_type" },
      {
        header: "分类",
        cell: ({ row }) => (
          <div>
            <div>{row.original.category_code}</div>
            <div className="text-xs text-slate-500">{row.original.category_name}</div>
          </div>
        ),
      },
      { header: "分级", accessorKey: "level" },
      { header: "敏感实体", accessorKey: "entity_count" },
      { header: "已处理", accessorKey: "processed_entity_count" },
      { header: "未处理", accessorKey: "unprocessed_entity_count" },
      {
        header: "处理状态",
        cell: ({ row }) => <StatusBadge value={row.original.process_status} />,
      },
      {
        header: "复检",
        cell: ({ row }) => <StatusBadge value={row.original.verification_status} />,
      },
      {
        header: "操作",
        cell: ({ row }) => (
          <div className="flex items-center gap-2">
            <a href={downloadUrl(row.original.id)} aria-label="下载脱敏文件">
              <Button variant="secondary" className="h-8 px-2">
                <Download className="h-4 w-4" />
              </Button>
            </a>
            <Button
              variant="ghost"
              className="h-8 px-2"
              aria-label="删除任务"
              onClick={() => removeTask(row.original.id)}
            >
              <Trash2 className="h-4 w-4 text-red-600" />
            </Button>
          </div>
        ),
      },
    ],
    [],
  );

  const table = useReactTable({
    data: tasks,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  const totals = useMemo(
    () => ({
      uploaded: total,
      processed: tasks.filter((task) => task.process_status === "处理成功").length,
      entities: tasks.reduce((sum, task) => sum + task.entity_count, 0),
      masked: tasks.reduce((sum, task) => sum + task.processed_entity_count, 0),
      verified: tasks.filter((task) => task.verification_status === "通过").length,
    }),
    [tasks, total],
  );

  return (
    <AppShell>
      <div className="border-b border-border bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-slate-950">DOCX/TXT 脱敏验证工作台</h1>
            <p className="mt-1 text-sm text-slate-500">本地客户验证版，不宣称生产可用；DOCX 预览为文本提取预览。</p>
          </div>
          <div className="rounded-md border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
            PoC v0.2 Web
          </div>
        </div>
      </div>

      <div className="space-y-4 p-6">
        <div className="grid grid-cols-5 gap-3">
          {[
            ["已上传文件数", totals.uploaded],
            ["已处理文件数", totals.processed],
            ["敏感实体数", totals.entities],
            ["已处理实体数", totals.masked],
            ["复检通过文件数", totals.verified],
          ].map(([label, value]) => (
            <Card key={label as string}>
              <CardContent className="p-3">
                <div className="text-xs text-slate-500">{label}</div>
                <div className="mt-1 text-2xl font-semibold text-slate-950">{value}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-[390px_1fr] gap-4">
          <Card>
            <CardHeader>
              <CardTitle>上传并创建任务</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-3" onSubmit={form.handleSubmit(onSubmit)}>
                <label className="block text-sm font-medium text-slate-700">
                  文件
                  <div className="mt-1 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4">
                    <input
                      className="sr-only"
                      id="file"
                      type="file"
                      accept=".docx,.txt"
                      onChange={(event) => {
                        const file = event.target.files?.[0] ?? null;
                        setSelectedFile(file);
                        if (file) form.setValue("file", file, { shouldValidate: true });
                      }}
                    />
                    <label htmlFor="file" className="flex cursor-pointer items-center gap-3">
                      <UploadCloud className="h-8 w-8 text-blue-600" />
                      <span>
                        <span className="block text-sm font-medium text-slate-900">
                          {selectedFile ? selectedFile.name : "选择 DOCX/TXT 文件"}
                        </span>
                        <span className="text-xs text-slate-500">
                          {selectedFile ? `${formatBytes(selectedFile.size)} · ${selectedFile.name.split(".").pop()?.toUpperCase()}` : "单次上传一个文件，最大 20MB"}
                        </span>
                      </span>
                    </label>
                  </div>
                </label>
                <FieldError message={form.formState.errors.file?.message} />

                <label className="block text-sm font-medium text-slate-700">
                  分类编码
                  <Input className="mt-1" {...form.register("category_code")} />
                </label>
                <FieldError message={form.formState.errors.category_code?.message} />
                <label className="block text-sm font-medium text-slate-700">
                  分类名称
                  <Input className="mt-1" {...form.register("category_name")} />
                </label>
                <FieldError message={form.formState.errors.category_name?.message} />
                <label className="block text-sm font-medium text-slate-700">
                  分级标签
                  <Select className="mt-1" {...form.register("level")}>
                    <option>第1级</option>
                    <option>第2级</option>
                    <option>第3级</option>
                    <option>第4级</option>
                  </Select>
                </label>
                <label className="block text-sm font-medium text-slate-700">
                  备注
                  <Textarea className="mt-1 min-h-20" {...form.register("note")} />
                </label>
                <div className="flex gap-2">
                  <Button type="submit" disabled={submitting}>
                    {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
                    上传并创建任务
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => {
                      form.reset({ category_code: "", category_name: "", level: "第3级", note: "" });
                      setSelectedFile(null);
                    }}
                  >
                    清空
                  </Button>
                </div>
                {stepIndex >= 0 && (
                  <ol className="grid grid-cols-1 gap-1 rounded-md bg-slate-50 p-2 text-xs text-slate-600">
                    {steps.map((step, index) => (
                      <li key={step} className={index <= stepIndex ? "font-medium text-blue-700" : ""}>
                        {index + 1}. {step}
                      </li>
                    ))}
                  </ol>
                )}
                {message && <div className="rounded-md bg-blue-50 px-3 py-2 text-sm text-blue-700">{message}</div>}
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>处理清单</CardTitle>
              <div className="flex gap-2">
                <a href={manifestUrl()}>
                  <Button variant="secondary">
                    <FileDown className="h-4 w-4" />
                    导出 CSV
                  </Button>
                </a>
                <a href={zipUrl()}>
                  <Button variant="secondary">
                    <FileArchive className="h-4 w-4" />
                    下载 ZIP
                  </Button>
                </a>
                <Button variant="ghost" onClick={refresh} disabled={loading}>
                  <RefreshCw className={loading ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="mb-3 grid grid-cols-6 gap-2">
                <div className="relative">
                  <Search className="pointer-events-none absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
                  <Input className="pl-8" placeholder="搜索文件名" value={search} onChange={(event) => setSearch(event.target.value)} />
                </div>
                <Select value={fileType} onChange={(event) => setFileType(event.target.value)}>
                  <option value="">全部格式</option>
                  <option value="DOCX">DOCX</option>
                  <option value="TXT">TXT</option>
                </Select>
                <Select value={levelFilter} onChange={(event) => setLevelFilter(event.target.value)}>
                  <option value="">全部分级</option>
                  <option>第1级</option>
                  <option>第2级</option>
                  <option>第3级</option>
                  <option>第4级</option>
                </Select>
                <Select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
                  <option value="">全部处理状态</option>
                  <option>处理成功</option>
                  <option>部分成功</option>
                  <option>处理失败</option>
                  <option>未发现敏感实体</option>
                </Select>
                <Select value={verificationFilter} onChange={(event) => setVerificationFilter(event.target.value)}>
                  <option value="">全部复检状态</option>
                  <option>通过</option>
                  <option>未通过</option>
                </Select>
                <Button variant="secondary" onClick={refresh}>应用筛选</Button>
              </div>
              <div className="overflow-hidden rounded-md border border-slate-200">
                <table className="w-full border-collapse text-sm">
                  <thead className="bg-slate-50 text-left text-xs font-medium text-slate-500">
                    {table.getHeaderGroups().map((headerGroup) => (
                      <tr key={headerGroup.id}>
                        {headerGroup.headers.map((header) => (
                          <th key={header.id} className="px-3 py-2">
                            {flexRender(header.column.columnDef.header, header.getContext())}
                          </th>
                        ))}
                      </tr>
                    ))}
                  </thead>
                  <tbody>
                    {table.getRowModel().rows.map((row) => (
                      <tr key={row.id} className="border-t border-slate-200 bg-white">
                        {row.getVisibleCells().map((cell) => (
                          <td key={cell.id} className="px-3 py-2 align-middle">
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </td>
                        ))}
                      </tr>
                    ))}
                    {!tasks.length && (
                      <tr>
                        <td className="px-3 py-10 text-center text-sm text-slate-500" colSpan={10}>
                          暂无处理记录
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return <p className="text-xs text-red-600">{message}</p>;
}
