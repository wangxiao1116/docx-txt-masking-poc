import { FileDetailView } from "@/components/file-detail-view";

export default async function FileDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <FileDetailView id={id} />;
}
