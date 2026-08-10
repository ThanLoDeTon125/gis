/**
 * Validator dữ liệu theo schema đích.
 *
 * Hai chỗ dùng:
 *   - gold của SAN-81: chặn dán nhãn lệch khuôn ngay từ đầu — dán xong cả corpus
 *     mới phát hiện lệch schema là phải dán lại, chi phí đắt nhất pipeline
 *   - output model ở SAN-79: bắt field bịa/thiếu trước khi đưa vào rule-engine
 *
 * Chỉ hỗ trợ tập con JSON Schema mà structured outputs chấp nhận (xem lint.ts)
 * cộng allOf/anyOf/oneOf. Schema nên qua lintSchema trước; validator này thi
 * hành schema đúng như viết, không kiểm lại các ràng buộc lint đã cấm.
 */

import { resolvePointer } from "./lint.ts";
import { isRecord, isScalar, type JsonRecord, type JsonValue } from "./types.ts";

export interface ValidationIssue {
  /** Đường dẫn tới chỗ sai trong DỮ LIỆU (không phải schema), vd "/dieu_khoan/3/ma". */
  path: string;
  message: string;
}

export function validateAgainstSchema(instance: JsonValue, schema: JsonRecord): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  check(instance, schema, schema, "", issues);
  return issues;
}

/** Đuổi hết chuỗi $ref tới schema thật. Ném lỗi nếu $ref tự trỏ vòng quanh. */
function deref(root: JsonRecord, node: JsonRecord, path: string): JsonRecord {
  const seen = new Set<JsonValue>();
  let current = node;
  while (typeof current["$ref"] === "string") {
    if (seen.has(current)) throw new Error(`Chuỗi $ref lặp vô hạn tại "${path}".`);
    seen.add(current);
    const target = resolvePointer(root, current["$ref"]);
    if (!isRecord(target)) {
      throw new Error(`$ref "${current["$ref"]}" tại "${path}" không trỏ tới schema hợp lệ.`);
    }
    current = target;
  }
  return current;
}

function jsonType(value: JsonValue): string {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  return typeof value;
}

function matchesType(value: JsonValue, type: string): boolean {
  if (type === "integer") return typeof value === "number" && Number.isInteger(value);
  return jsonType(value) === type;
}

/** Chạy thử một nhánh schema, chỉ cần biết đậu/rớt — dùng cho anyOf/oneOf. */
function passes(value: JsonValue, branch: JsonRecord, root: JsonRecord): boolean {
  const trial: ValidationIssue[] = [];
  check(value, branch, root, "", trial);
  return trial.length === 0;
}

function check(
  value: JsonValue,
  schemaNode: JsonRecord,
  root: JsonRecord,
  path: string,
  issues: ValidationIssue[],
): void {
  const schema = deref(root, schemaNode, path);

  const rawType = "type" in schema ? schema["type"] : undefined;
  const types =
    typeof rawType === "string"
      ? [rawType]
      : Array.isArray(rawType)
        ? rawType.filter((entry): entry is string => typeof entry === "string")
        : null;
  if (types !== null && !types.some((type) => matchesType(value, type))) {
    issues.push({
      path,
      message: `kiểu ${jsonType(value)}, schema yêu cầu ${types.join(" | ")}`,
    });
    // Sai kiểu rồi thì kiểm tra sâu hơn chỉ sinh nhiễu — dừng nhánh này.
    return;
  }

  const enumValues = "enum" in schema ? schema["enum"] : undefined;
  if (
    Array.isArray(enumValues) &&
    !enumValues.some((entry) => isScalar(entry) && entry === value)
  ) {
    issues.push({
      path,
      message: `giá trị ${JSON.stringify(value)} không nằm trong enum`,
    });
  }

  const allOf = "allOf" in schema ? schema["allOf"] : undefined;
  if (Array.isArray(allOf)) {
    for (const branch of allOf) {
      if (isRecord(branch)) check(value, branch, root, path, issues);
    }
  }
  const anyOf = "anyOf" in schema ? schema["anyOf"] : undefined;
  if (Array.isArray(anyOf)) {
    const branches = anyOf.filter(isRecord);
    if (!branches.some((branch) => passes(value, branch, root))) {
      issues.push({ path, message: "không khớp nhánh nào của anyOf" });
    }
  }
  const oneOf = "oneOf" in schema ? schema["oneOf"] : undefined;
  if (Array.isArray(oneOf)) {
    const matched = oneOf.filter(isRecord).filter((branch) => passes(value, branch, root)).length;
    if (matched !== 1) {
      issues.push({ path, message: `khớp ${matched} nhánh của oneOf, yêu cầu đúng 1` });
    }
  }

  if (isRecord(value)) {
    const required = "required" in schema ? schema["required"] : undefined;
    if (Array.isArray(required)) {
      for (const field of required) {
        if (typeof field === "string" && !(field in value)) {
          issues.push({ path, message: `thiếu field bắt buộc "${field}"` });
        }
      }
    }
    const properties = "properties" in schema ? schema["properties"] : undefined;
    if (isRecord(properties)) {
      for (const [key, child] of Object.entries(value)) {
        if (key in properties) {
          const childSchema = properties[key];
          if (isRecord(childSchema)) check(child, childSchema, root, `${path}/${key}`, issues);
        } else if (schema["additionalProperties"] === false) {
          issues.push({
            path: `${path}/${key}`,
            message: `field "${key}" không có trong schema (additionalProperties: false)`,
          });
        }
      }
    }
  }

  if (Array.isArray(value)) {
    const items = "items" in schema ? schema["items"] : undefined;
    if (isRecord(items)) {
      value.forEach((child, index) => check(child, items, root, `${path}/${index}`, issues));
    }
    const minItems = "minItems" in schema ? schema["minItems"] : undefined;
    if (typeof minItems === "number" && value.length < minItems) {
      issues.push({
        path,
        message: `mảng có ${value.length} phần tử, schema yêu cầu tối thiểu ${minItems}`,
      });
    }
  }
}
