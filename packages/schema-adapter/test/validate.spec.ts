import { describe, expect, it } from "vitest";

import { validateAgainstSchema } from "../src/validate.ts";
import type { JsonRecord, JsonValue } from "../src/types.ts";

/** Schema mảng phẳng — cùng hình dạng với fixture bên lint.spec. */
const schema: JsonRecord = {
  type: "object",
  additionalProperties: false,
  required: ["ten_tieu_chuan", "dieu_khoan"],
  properties: {
    ten_tieu_chuan: { type: "string" },
    dieu_khoan: {
      type: "array",
      items: { $ref: "#/$defs/dieu" },
    },
  },
  $defs: {
    dieu: {
      type: "object",
      additionalProperties: false,
      required: ["ma", "ma_cha", "noi_dung"],
      properties: {
        ma: { type: "string" },
        ma_cha: { type: ["string", "null"] },
        noi_dung: { type: "string" },
        muc_do: { type: "string", enum: ["chinh_yeu", "thu_yeu"] },
        thu_tu: { type: "integer" },
      },
    },
  },
};

const validDoc: JsonValue = {
  ten_tieu_chuan: "VietGAP trồng trọt",
  dieu_khoan: [
    { ma: "1", ma_cha: null, noi_dung: "Phần 1", muc_do: "chinh_yeu", thu_tu: 1 },
    { ma: "1.1", ma_cha: "1", noi_dung: "Điều 1.1" },
  ],
};

describe("validateAgainstSchema", () => {
  it("tài liệu đúng khuôn thì sạch, $ref nội bộ resolve được", () => {
    expect(validateAgainstSchema(validDoc, schema)).toEqual([]);
  });

  it("bắt thiếu field bắt buộc", () => {
    const issues = validateAgainstSchema(
      { ten_tieu_chuan: "x", dieu_khoan: [{ ma: "1", ma_cha: null }] },
      schema,
    );
    expect(issues).toHaveLength(1);
    expect(issues[0]!.path).toBe("/dieu_khoan/0");
    expect(issues[0]!.message).toContain('"noi_dung"');
  });

  it("bắt sai kiểu, đường dẫn trỏ đúng phần tử lỗi", () => {
    const issues = validateAgainstSchema(
      { ten_tieu_chuan: "x", dieu_khoan: [{ ma: 1, ma_cha: null, noi_dung: "a" }] },
      schema,
    );
    expect(issues).toHaveLength(1);
    expect(issues[0]!.path).toBe("/dieu_khoan/0/ma");
  });

  it("bắt field lạ khi additionalProperties false — model bịa field là lộ ngay", () => {
    const issues = validateAgainstSchema(
      {
        ten_tieu_chuan: "x",
        dieu_khoan: [{ ma: "1", ma_cha: null, noi_dung: "a", ghi_chu: "bịa" }],
      },
      schema,
    );
    expect(issues).toHaveLength(1);
    expect(issues[0]!.path).toBe("/dieu_khoan/0/ghi_chu");
  });

  it("bắt giá trị ngoài enum", () => {
    const issues = validateAgainstSchema(
      {
        ten_tieu_chuan: "x",
        dieu_khoan: [{ ma: "1", ma_cha: null, noi_dung: "a", muc_do: "tuy_hung" }],
      },
      schema,
    );
    expect(issues).toHaveLength(1);
    expect(issues[0]!.message).toContain("enum");
  });

  it("integer không nhận số lẻ", () => {
    const issues = validateAgainstSchema(
      {
        ten_tieu_chuan: "x",
        dieu_khoan: [{ ma: "1", ma_cha: null, noi_dung: "a", thu_tu: 1.5 }],
      },
      schema,
    );
    expect(issues).toHaveLength(1);
    expect(issues[0]!.path).toBe("/dieu_khoan/0/thu_tu");
  });

  it("type dạng mảng nhận cả hai kiểu — ma_cha string | null", () => {
    expect(
      validateAgainstSchema(
        { ten_tieu_chuan: "x", dieu_khoan: [{ ma: "1", ma_cha: "0", noi_dung: "a" }] },
        schema,
      ),
    ).toEqual([]);
  });

  it("thi hành minItems đúng như schema viết", () => {
    const withMin: JsonRecord = {
      type: "array",
      minItems: 1,
      items: { type: "string" },
    };
    expect(validateAgainstSchema([], withMin)).toHaveLength(1);
    expect(validateAgainstSchema(["a"], withMin)).toEqual([]);
  });

  it("anyOf đậu khi khớp một nhánh, rớt khi không nhánh nào", () => {
    const either: JsonRecord = {
      anyOf: [{ type: "string" }, { type: "number" }],
    };
    expect(validateAgainstSchema("a", either)).toEqual([]);
    expect(validateAgainstSchema(true, either)).toHaveLength(1);
  });
});
