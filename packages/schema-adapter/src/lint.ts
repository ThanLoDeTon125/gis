/**
 * Linter: schema có dùng được với structured outputs không.
 *
 * Danh sách tính năng bị chặn lấy từ khảo sát SAN-80 — dùng là API trả 400:
 *
 *   - recursive schema — $ref trỏ ngược lên tổ tiên của chính nó
 *   - external $ref — trỏ ra ngoài file
 *   - complex types trong enum
 *   - ràng buộc số: minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf
 *   - ràng buộc chuỗi: minLength, maxLength
 *   - ràng buộc mảng ngoài minItems 0/1
 *   - additionalProperties khác false
 *
 * Mục đích trước mắt: chạy trên file JSON trong resource của SAN-78 (đã chốt là
 * schema đích, 10/08/2026) ngay khi file về repo — biết ngay schema gửi thẳng
 * cho API được, hay dính đệ quy và phải đi đường mảng phẳng của flatten.ts.
 */

import { isRecord, isScalar, type JsonRecord, type JsonValue } from "./types.ts";

export type LintLevel = "error" | "warning";

export interface LintFinding {
  level: LintLevel;
  /** JSON pointer tới chỗ vướng, vd "#/properties/dieu_khoan/items". */
  path: string;
  rule: string;
  message: string;
}

export interface LintReport {
  findings: LintFinding[];
  /** true khi không có finding mức error — schema gửi thẳng cho API được. */
  ok: boolean;
}

/** Resolve JSON pointer nội bộ dạng "#/a/b". Trả undefined nếu không trỏ tới đâu. */
export function resolvePointer(root: JsonRecord, ref: string): JsonValue | undefined {
  if (!ref.startsWith("#")) return undefined;
  let node: JsonValue = root;
  const segments = ref
    .slice(1)
    .split("/")
    .filter((segment) => segment.length > 0)
    .map((segment) => segment.replaceAll("~1", "/").replaceAll("~0", "~"));
  for (const segment of segments) {
    if (isRecord(node) && segment in node) {
      node = node[segment];
    } else if (Array.isArray(node)) {
      const index = Number(segment);
      if (!Number.isInteger(index) || index < 0 || index >= node.length) return undefined;
      node = node[index]!;
    } else {
      return undefined;
    }
  }
  return node;
}

const NUMERIC_CONSTRAINTS = [
  "minimum",
  "maximum",
  "exclusiveMinimum",
  "exclusiveMaximum",
  "multipleOf",
] as const;
const STRING_CONSTRAINTS = ["minLength", "maxLength"] as const;
const ARRAY_CONSTRAINTS = [
  "maxItems",
  "uniqueItems",
  "contains",
  "minContains",
  "maxContains",
] as const;
const COMBINERS = ["allOf", "anyOf", "oneOf"] as const;

export function lintSchema(schema: JsonRecord): LintReport {
  const findings: LintFinding[] = [];
  walk(schema, schema, "#", [], findings);

  // Một $defs được tham chiếu từ nhiều chỗ sẽ bị duyệt nhiều lần (finding báo
  // tại vị trí của def, không phải chỗ gọi) — gộp finding trùng.
  const seen = new Set<string>();
  const unique = findings.filter((finding) => {
    const key = `${finding.rule}|${finding.path}|${finding.message}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  return { findings: unique, ok: unique.every((finding) => finding.level !== "error") };
}

function walk(
  root: JsonRecord,
  node: JsonValue,
  path: string,
  ancestors: readonly JsonValue[],
  findings: LintFinding[],
): void {
  if (!isRecord(node)) return;
  const next = [...ancestors, node];

  const ref = node["$ref"];
  if (typeof ref === "string") {
    if (!ref.startsWith("#")) {
      findings.push({
        level: "error",
        path,
        rule: "external-ref",
        message: `$ref "${ref}" trỏ ra ngoài file — không được hỗ trợ, phải inline schema vào một file.`,
      });
    } else {
      const target = resolvePointer(root, ref);
      if (target === undefined) {
        findings.push({
          level: "error",
          path,
          rule: "broken-ref",
          message: `$ref "${ref}" không trỏ tới đâu trong schema.`,
        });
      } else if (target === node || ancestors.includes(target)) {
        findings.push({
          level: "error",
          path,
          rule: "recursive-ref",
          message:
            `$ref "${ref}" trỏ ngược lên tổ tiên — schema đệ quy không được hỗ trợ. ` +
            "Đi đường mảng phẳng ma/ma_cha (flatten.ts).",
        });
      } else {
        // Duyệt tiếp với path là vị trí thật của def — finding trong $defs
        // báo đúng chỗ cần sửa.
        walk(root, target, ref, next, findings);
      }
    }
  }

  for (const keyword of NUMERIC_CONSTRAINTS) {
    if (keyword in node) {
      findings.push({
        level: "error",
        path: `${path}/${keyword}`,
        rule: "numeric-constraint",
        message: `"${keyword}" không được hỗ trợ — bỏ khỏi schema, kiểm ở tầng ứng dụng.`,
      });
    }
  }
  for (const keyword of STRING_CONSTRAINTS) {
    if (keyword in node) {
      findings.push({
        level: "error",
        path: `${path}/${keyword}`,
        rule: "string-constraint",
        message:
          `"${keyword}" không được hỗ trợ — không ép được ràng buộc như "chuỗi không rỗng" ` +
          "bằng schema, phải kiểm ở tầng ứng dụng.",
      });
    }
  }
  for (const keyword of ARRAY_CONSTRAINTS) {
    if (keyword in node) {
      findings.push({
        level: "error",
        path: `${path}/${keyword}`,
        rule: "array-constraint",
        message: `"${keyword}" không được hỗ trợ — ràng buộc mảng chỉ được dùng minItems 0 hoặc 1.`,
      });
    }
  }
  const minItems = node["minItems"];
  if (typeof minItems === "number" && minItems > 1) {
    findings.push({
      level: "error",
      path: `${path}/minItems`,
      rule: "array-constraint",
      message: `minItems ${minItems} không được hỗ trợ — chỉ được 0 hoặc 1.`,
    });
  }

  const enumValues = node["enum"];
  if (Array.isArray(enumValues) && !enumValues.every(isScalar)) {
    findings.push({
      level: "error",
      path: `${path}/enum`,
      rule: "enum-complex",
      message: "enum chứa giá trị không phải scalar — chỉ string/number/boolean/null được hỗ trợ.",
    });
  }

  const isObjectSchema = node["type"] === "object" || isRecord(node["properties"]);
  if (isObjectSchema) {
    const additional = "additionalProperties" in node ? node["additionalProperties"] : undefined;
    if (additional === undefined) {
      findings.push({
        level: "warning",
        path,
        rule: "additional-properties",
        message:
          'Object chưa khai "additionalProperties": false — nên khai rõ để model không tự thêm field.',
      });
    } else if (additional !== false) {
      findings.push({
        level: "error",
        path: `${path}/additionalProperties`,
        rule: "additional-properties",
        message: '"additionalProperties" khác false không được hỗ trợ.',
      });
    }
  }

  const properties = node["properties"];
  if (isRecord(properties)) {
    for (const [key, child] of Object.entries(properties)) {
      walk(root, child, `${path}/properties/${key}`, next, findings);
    }
  }
  const items = node["items"];
  if (isRecord(items)) {
    walk(root, items, `${path}/items`, next, findings);
  } else if (Array.isArray(items)) {
    items.forEach((child, index) => walk(root, child, `${path}/items/${index}`, next, findings));
  }
  for (const combiner of COMBINERS) {
    const branches = node[combiner];
    if (Array.isArray(branches)) {
      branches.forEach((child, index) =>
        walk(root, child, `${path}/${combiner}/${index}`, next, findings),
      );
    }
  }
}
