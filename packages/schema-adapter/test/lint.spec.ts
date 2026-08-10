import { describe, expect, it } from "vitest";

import { lintSchema } from "../src/lint.ts";
import type { JsonRecord } from "../src/types.ts";

/** Schema mảng phẳng đúng kiểu SAN-80 khuyến nghị — không được vướng gì. */
const flatSchema: JsonRecord = {
  type: "object",
  additionalProperties: false,
  required: ["dieu_khoan"],
  properties: {
    dieu_khoan: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["ma", "ma_cha", "noi_dung"],
        properties: {
          ma: { type: "string" },
          ma_cha: { type: ["string", "null"] },
          noi_dung: { type: "string" },
          bat_buoc: { type: "boolean" },
          muc_do: { type: "string", enum: ["chinh_yeu", "thu_yeu", "khuyen_nghi"] },
        },
      },
    },
  },
};

/** Cây đệ quy qua $defs — đúng kiểu schema mà văn bản tiêu chuẩn hay được mô hình hoá. */
const recursiveSchema: JsonRecord = {
  type: "object",
  additionalProperties: false,
  properties: {
    muc: { type: "array", items: { $ref: "#/$defs/muc" } },
  },
  $defs: {
    muc: {
      type: "object",
      additionalProperties: false,
      properties: {
        ma: { type: "string" },
        muc_con: { type: "array", items: { $ref: "#/$defs/muc" } },
      },
    },
  },
};

const rules = (schema: JsonRecord): string[] =>
  lintSchema(schema).findings.map((finding) => finding.rule);

describe("lintSchema", () => {
  it("schema mảng phẳng chuẩn thì sạch", () => {
    const report = lintSchema(flatSchema);
    expect(report.findings).toEqual([]);
    expect(report.ok).toBe(true);
  });

  it("bắt schema đệ quy qua $ref", () => {
    const report = lintSchema(recursiveSchema);
    expect(report.ok).toBe(false);
    expect(report.findings.some((finding) => finding.rule === "recursive-ref")).toBe(true);
  });

  it("bắt $ref trỏ thẳng về root", () => {
    expect(rules({ $ref: "#" })).toContain("recursive-ref");
  });

  it("bắt external $ref", () => {
    expect(
      rules({
        type: "object",
        additionalProperties: false,
        properties: { muc: { $ref: "common.json#/muc" } },
      }),
    ).toContain("external-ref");
  });

  it("bắt $ref gãy", () => {
    expect(
      rules({
        type: "object",
        additionalProperties: false,
        properties: { muc: { $ref: "#/$defs/khong_ton_tai" } },
      }),
    ).toContain("broken-ref");
  });

  it("bắt ràng buộc số, chuỗi, mảng", () => {
    const found = rules({
      type: "object",
      additionalProperties: false,
      properties: {
        diem: { type: "number", minimum: 0 },
        ten: { type: "string", minLength: 1 },
        danh_sach: { type: "array", maxItems: 5, minItems: 2, items: { type: "string" } },
      },
    });
    expect(found).toContain("numeric-constraint");
    expect(found).toContain("string-constraint");
    // maxItems và minItems 2 là hai finding riêng
    expect(found.filter((rule) => rule === "array-constraint")).toHaveLength(2);
  });

  it("minItems 0 hoặc 1 thì được phép", () => {
    const report = lintSchema({
      type: "object",
      additionalProperties: false,
      properties: {
        bat_buoc: { type: "array", minItems: 1, items: { type: "string" } },
        tuy_chon: { type: "array", minItems: 0, items: { type: "string" } },
      },
    });
    expect(report.findings).toEqual([]);
  });

  it("thiếu additionalProperties chỉ là cảnh báo, không chặn", () => {
    const report = lintSchema({ type: "object", properties: { ma: { type: "string" } } });
    expect(report.ok).toBe(true);
    expect(report.findings).toHaveLength(1);
    expect(report.findings[0]!.level).toBe("warning");
    expect(report.findings[0]!.rule).toBe("additional-properties");
  });

  it("additionalProperties khác false là lỗi", () => {
    const report = lintSchema({
      type: "object",
      additionalProperties: true,
      properties: { ma: { type: "string" } },
    });
    expect(report.ok).toBe(false);
    expect(report.findings[0]!.rule).toBe("additional-properties");
  });

  it("bắt enum chứa giá trị phức", () => {
    expect(
      rules({
        type: "object",
        additionalProperties: false,
        properties: { loai: { enum: [{ ma: "a" }, "b"] } },
      }),
    ).toContain("enum-complex");
  });

  it("finding trong $defs dùng chung không bị báo trùng", () => {
    const report = lintSchema({
      type: "object",
      additionalProperties: false,
      properties: {
        a: { $ref: "#/$defs/ten" },
        b: { $ref: "#/$defs/ten" },
      },
      $defs: { ten: { type: "string", minLength: 1 } },
    });
    expect(report.findings.filter((finding) => finding.rule === "string-constraint")).toHaveLength(
      1,
    );
  });
});
