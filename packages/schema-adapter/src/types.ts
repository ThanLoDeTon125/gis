/**
 * Kiểu JSON dùng chung cho cả package.
 *
 * Schema đích (file JSON trong resource SAN-78) được đối xử như dữ liệu JSON
 * thuần và duyệt động, không khai interface cứng — schema là đầu vào bên ngoài,
 * package này không được phép giả định trước hình dạng của nó.
 */

export type JsonValue =
  | null
  | boolean
  | number
  | string
  | JsonValue[]
  | { [key: string]: JsonValue };

export type JsonRecord = { [key: string]: JsonValue };

export function isRecord(value: JsonValue | undefined): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function isScalar(value: JsonValue): value is null | boolean | number | string {
  return value === null || typeof value !== "object";
}
