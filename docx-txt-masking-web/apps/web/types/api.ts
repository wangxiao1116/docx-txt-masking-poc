export type ApiResponse<T> = {
  code: number;
  message: string;
  data: T;
};

export type FileTask = {
  id: string;
  original_file_name: string;
  output_file_name: string | null;
  file_type: "DOCX" | "TXT";
  file_size: number;
  category_code: string;
  category_name: string;
  level: string;
  label_source: string;
  note: string;
  entity_count: number;
  processed_entity_count: number;
  unprocessed_entity_count: number;
  process_status: string;
  verification_status: string;
  error_message: string;
  created_at: string;
  updated_at: string;
};

export type EntityRecord = {
  id: number;
  entity_type: string;
  masked_original_value: string;
  masked_value: string;
  location: string;
  extractor: string;
  format_valid: boolean;
  checksum_valid: boolean | null;
  processed: boolean;
  created_at: string;
};

export type FileTaskDetail = FileTask & {
  entities: EntityRecord[];
  verification: Record<string, unknown>;
  mappings: Array<Record<string, string>>;
  metadata: Record<string, unknown>;
};

export type FileListPayload = {
  items: FileTask[];
  total: number;
  page: number;
  page_size: number;
};
