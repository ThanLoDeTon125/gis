import { describe, expect, it } from "vitest";

import { flatToTree, treeToFlat } from "../src/flatten.ts";
import type { JsonValue } from "../src/types.ts";

const shape = { childrenKey: "muc_con" };

/** Cây kiểu VietGAP thu nhỏ: phần → điều → khoản, node lá không mang muc_con. */
const tree: JsonValue[] = [
  {
    ma: "1",
    noi_dung: "Phần 1",
    muc_con: [
      {
        ma: "1.1",
        noi_dung: "Điều 1.1",
        muc_con: [{ ma: "1.1.1", noi_dung: "Khoản a", bat_buoc: true }],
      },
      { ma: "1.2", noi_dung: "Điều 1.2" },
    ],
  },
  { ma: "2", noi_dung: "Phần 2" },
];

describe("treeToFlat", () => {
  it("duyệt pre-order, gắn ma_cha đúng", () => {
    const flat = treeToFlat(tree, shape);
    expect(flat.map((item) => item["ma"])).toEqual(["1", "1.1", "1.1.1", "1.2", "2"]);
    expect(flat.map((item) => item["ma_cha"])).toEqual([null, "1", "1.1", "1", null]);
    // field con không được lọt vào dạng phẳng
    expect(flat.every((item) => !("muc_con" in item))).toBe(true);
    // field khác giữ nguyên
    expect(flat[2]!["bat_buoc"]).toBe(true);
  });

  it("ném lỗi khi mã trùng", () => {
    const duplicated: JsonValue[] = [{ ma: "1" }, { ma: "1" }];
    expect(() => treeToFlat(duplicated, shape)).toThrow(/hai lần/);
  });

  it("ném lỗi khi node thiếu mã", () => {
    expect(() => treeToFlat([{ noi_dung: "mồ côi" }], shape)).toThrow(/không có "ma"/);
  });
});

describe("flatToTree", () => {
  it("round-trip khớp cây gốc từng byte", () => {
    const result = flatToTree(treeToFlat(tree, shape), shape);
    expect(result.roots).toEqual(tree);
    expect(result.orphans).toEqual([]);
    expect(result.cycles).toEqual([]);
  });

  it("ma_cha trỏ bậy thì nâng làm root và báo orphan, không vứt dữ liệu", () => {
    const result = flatToTree(
      [
        { ma: "1", ma_cha: null },
        { ma: "x", ma_cha: "khong_ton_tai" },
      ],
      shape,
    );
    expect(result.roots.map((root) => root["ma"])).toEqual(["1", "x"]);
    expect(result.orphans).toEqual(["x"]);
  });

  it("chu trình ma_cha bị cắt, cây vẫn dựng được", () => {
    const result = flatToTree(
      [
        { ma: "a", ma_cha: "b" },
        { ma: "b", ma_cha: "a" },
      ],
      shape,
    );
    expect(result.cycles).toEqual(["a"]);
    expect(result.roots).toHaveLength(1);
    expect(result.roots[0]!["ma"]).toBe("a");
    expect(result.roots[0]!["muc_con"]).toEqual([{ ma: "b" }]);
  });

  it("ném lỗi khi mã trùng", () => {
    expect(() => flatToTree([{ ma: "1" }, { ma: "1" }], shape)).toThrow(/hai lần/);
  });
});
