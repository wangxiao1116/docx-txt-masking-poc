"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, Download, Eye, EyeOff, RefreshCw } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { downloadUrl, getFileDetail, getPreview } from "@/lib/api";
import { formatBytes, maskIdCards } from "@/lib/utils";
import type { FileTaskDetail } from "@/types/api";

export function FileDetailView({ id }: { id: string }) {
  const [detail, setDetail] = useState<FileTaskDetail | null>(null);
  const [originalPreview, setOriginalPreview] = useState("");
  const [maskedPreview, setMaskedPreview] = useState("");
  const [showOriginal, setShowOriginal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  async function load() {
    setLoading(true);
    setMessage("");
    try {
      const [task, original, masked] = await Promise.all([
        getFileDetail(id),
        getPreview(id, "original"),
        getPreview(id, "masked"),
      ]);
      setDetail(task);
      setOriginalPreview(original.text);
      setMaskedPreview(masked.text);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "详情加载失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [id]);

  const safeOriginalPreview = useMemo(
    () => (showOriginal ? originalPreview : maskIdCards(originalPreview)),
    [originalPreview, showOriginal],
  );

  function toggleOriginal() {
    if (showOriginal) {
      setShowOriginal(false);
      return;
    }
    if (window.confirm("原文预览可能包含完整身份证号码。确认显示原值？")) {
      setShowOriginal(true);
    }
  }

  return (
    <AppShell>
      <div className="border-b border-border bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <Link className="inline-flex items-center gap-2 text-sm text-blue-700 hover:underline" href="/">
              <ArrowLeft className="h-4 w-4" />
              返回工作台
            </Link>
            <h1 className="mt-2 text-xl font-semibold text-slate-950">文件处理详情</h1>
            <p className="mt-1 text-sm text-slate-500">DOCX 预览为文本提取预览，不是完整 Word 版式渲染。</p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={load} disabled={loading}>
              <RefreshCw className={loading ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
              刷新
            </Button>
            <a href={downloadUrl(id)}>
              <Button>
                <Download className="h-4 w-4" />
                下载脱敏文件
              </Button>
            </a>
          </div>
        </div>
      </div>

      <div className="space-y-4 p-6">
        {message && <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{message}</div>}
        {detail && (
          <>
            <div className="grid grid-cols-4 gap-3">
              <Metric label="文件名" value={detail.original_file_name} />
              <Metric label="文件大小" value={formatBytes(detail.file_size)} />
              <Metric label="处理状态" value={<StatusBadge value={detail.process_status} />} />
              <Metric label="复检状态" value={<StatusBadge value={detail.verification_status} />} />
            </div>

            <div className="grid grid-cols-[360px_1fr] gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>基础信息与标签</CardTitle>
                </CardHeader>
                <CardContent>
                  <dl className="space-y-3 text-sm">
                    <Info label="格式" value={detail.file_type} />
                    <Info label="分类编码" value={detail.category_code} />
                    <Info label="分类名称" value={detail.category_name} />
                    <Info label="分级标签" value={detail.level} />
                    <Info label="标签来源" value={detail.label_source} />
                    <Info label="上传时间" value={new Date(detail.created_at).toLocaleString()} />
                    <Info label="备注" value={detail.note || "-"} />
                  </dl>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>处理时间线</CardTitle>
                  <div className="text-xs text-slate-500">同步处理链路</div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-7 gap-2 text-xs">
                    {["上传", "解析", "提取实体", "执行遮蔽", "文件重建", "输出复检", "完成"].map((step) => (
                      <div key={step} className="rounded-md bg-blue-50 px-2 py-2 text-center font-medium text-blue-700">
                        {step}
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 grid grid-cols-3 gap-3">
                    <InlineMetric label="敏感实体数量" value={detail.entity_count} />
                    <InlineMetric label="已处理实体" value={detail.processed_entity_count} />
                    <InlineMetric label="未处理实体" value={detail.unprocessed_entity_count} />
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>原文文本预览</CardTitle>
                  <Button variant="secondary" onClick={toggleOriginal}>
                    {showOriginal ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    {showOriginal ? "隐藏原值" : "显示原值"}
                  </Button>
                </CardHeader>
                <CardContent>
                  <pre className="min-h-72 max-h-[460px] overflow-auto rounded-md bg-slate-950 p-3 text-xs leading-5 text-slate-100">
                    {safeOriginalPreview || "无可预览文本"}
                  </pre>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>脱敏后文本预览</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="min-h-72 max-h-[460px] overflow-auto rounded-md bg-slate-950 p-3 text-xs leading-5 text-slate-100">
                    {maskedPreview || "无可预览文本"}
                  </pre>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>敏感实体清单</CardTitle>
                </CardHeader>
                <CardContent>
                  <table className="w-full text-sm">
                    <thead className="text-left text-xs text-slate-500">
                      <tr>
                        <th className="py-2">类型</th>
                        <th>掩码原值</th>
                        <th>位置</th>
                        <th>校验</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.entities.map((entity) => (
                        <tr key={entity.id} className="border-t border-slate-200">
                          <td className="py-2">{entity.entity_type}</td>
                          <td>{entity.masked_original_value}</td>
                          <td>{entity.location}</td>
                          <td>{entity.checksum_valid === null ? "-" : entity.checksum_valid ? "通过" : "未通过"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>原值—遮蔽值映射与复检</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <table className="w-full text-sm">
                    <thead className="text-left text-xs text-slate-500">
                      <tr>
                        <th className="py-2">掩码原值</th>
                        <th>遮蔽值</th>
                        <th>位置</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.mappings.map((mapping, index) => (
                        <tr key={index} className="border-t border-slate-200">
                          <td className="py-2">{mapping.masked_original_value}</td>
                          <td>{mapping.masked_value}</td>
                          <td>{mapping.location}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <pre className="max-h-72 overflow-auto rounded-md bg-slate-50 p-3 text-xs text-slate-700">
                    {JSON.stringify(detail.verification, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}

function Metric({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <Card>
      <CardContent className="p-3">
        <div className="text-xs text-slate-500">{label}</div>
        <div className="mt-1 truncate text-lg font-semibold text-slate-950">{value}</div>
      </CardContent>
    </Card>
  );
}

function Info({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <dt className="text-xs text-slate-500">{label}</dt>
      <dd className="mt-1 font-medium text-slate-900">{value}</dd>
    </div>
  );
}

function InlineMetric({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-slate-950">{value}</div>
    </div>
  );
}
