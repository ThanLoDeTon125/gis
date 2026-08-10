/**
 * Làm phẳng cây điều khoản ↔ dựng lại cây.
 *
 * Structured outputs không hỗ trợ schema đệ quy (xem lint.ts), trong khi văn
 * bản tiêu chuẩn lồng nhau tự nhiên: phần → chương → điều → khoản → điểm. Cách
 * né được khảo sát SAN-80 khuyến nghị: model trả MẢNG PHẲNG, mỗi phần tử mang
 * mã của mình và mã cha (ma/ma_cha); cấu trúc cây dựng lại ở phía đọc.
 *
 * Cặp hàm này là hai chiều của quy ước đó:
 *   - treeToFlat  cây (schema đích, gold dán tay theo cây) → mảng phẳng
 *   - flatToTree  mảng phẳng (output model) → cây theo schema đích
 *
 * childrenKey không có default: tên field chứa con do schema đích của SAN-78
 * quyết định, chưa có file thì chưa chốt được — bắt người gọi khai rõ.
 */

import { isRecord, type JsonRecord, type JsonValue } from "./types.ts";

export interface TreeShape {
  /** Field mã định danh trong mỗi node. Mặc định "ma". */
  idKey?: string;
  /** Field trỏ về mã cha ở dạng phẳng. Mặc định "ma_cha". */
  parentKey?: string;
  /** Field chứa mảng con ở dạng cây — tên do schema đích quyết định, phải khai rõ. */
  childrenKey: string;
}

interface ResolvedShape {
  idKey: string;
  parentKey: string;
  childrenKey: string;
}

const resolveShape = (shape: TreeShape): ResolvedShape => ({
  idKey: shape.idKey ?? "ma",
  parentKey: shape.parentKey ?? "ma_cha",
  childrenKey: shape.childrenKey,
});

function idOf(node: JsonRecord, idKey: string, path: string): string {
  const raw = idKey in node ? node[idKey] : null;
  if (typeof raw === "string" && raw.trim() !== "") return raw;
  if (typeof raw === "number") return String(raw);
  throw new Error(`Node tại ${path} không có "${idKey}" dạng chuỗi/số — không xử lý được.`);
}

/** Copy node, bỏ một field. */
function omit(node: JsonRecord, excludedKey: string): JsonRecord {
  const rest: JsonRecord = {};
  for (const [key, value] of Object.entries(node)) {
    if (key !== excludedKey) rest[key] = value;
  }
  return rest;
}

/**
 * Cây → mảng phẳng, duyệt pre-order nên thứ tự đọc của văn bản được giữ nguyên.
 * Ném lỗi khi mã trùng hoặc thiếu — mã không sạch thì dạng phẳng mất thông tin,
 * lặng lẽ cho qua sẽ hỏng dữ liệu ở tầng sau.
 */
export function treeToFlat(roots: readonly JsonValue[], shapeInput: TreeShape): JsonRecord[] {
  const shape = resolveShape(shapeInput);
  const out: JsonRecord[] = [];
  const seen = new Set<string>();

  const visit = (node: JsonValue, parentId: string | null, path: string): void => {
    if (!isRecord(node)) throw new Error(`Node tại ${path} không phải object.`);
    const id = idOf(node, shape.idKey, path);
    if (seen.has(id)) {
      throw new Error(`Mã "${id}" xuất hiện hai lần — mã trùng thì không dựng lại cây được.`);
    }
    seen.add(id);
    out.push({ ...omit(node, shape.childrenKey), [shape.parentKey]: parentId });

    const children = shape.childrenKey in node ? node[shape.childrenKey] : undefined;
    if (children === undefined) return;
    if (!Array.isArray(children)) {
      throw new Error(`"${shape.childrenKey}" tại ${path} phải là mảng.`);
    }
    children.forEach((child, index) => visit(child, id, `${path}/${shape.childrenKey}/${index}`));
  };

  roots.forEach((root, index) => visit(root, null, `/${index}`));
  return out;
}

export interface TreeResult {
  roots: JsonRecord[];
  /** Mã có parent trỏ tới node không tồn tại — được nâng làm root thay vì vứt bỏ. */
  orphans: string[];
  /** Mã bị cắt khỏi chu trình parent để cây dựng được. */
  cycles: string[];
}

/**
 * Mảng phẳng → cây. Đầu vào là output model nên phải chịu được dữ liệu bẩn:
 * ma_cha trỏ bậy (orphan) hay trỏ vòng (cycle) không ném lỗi mà được vá cho
 * cây dựng được, kèm danh sách mã hỏng để tầng eval tính điểm phạt.
 * Chỉ mã trùng mới ném lỗi — trùng mã thì không còn cách vá nào đúng.
 */
export function flatToTree(items: readonly JsonValue[], shapeInput: TreeShape): TreeResult {
  const shape = resolveShape(shapeInput);

  interface Slot {
    node: JsonRecord;
    id: string;
    parentId: string | null;
    children: Slot[];
  }

  const slots: Slot[] = [];
  const byId = new Map<string, Slot>();

  items.forEach((item, index) => {
    if (!isRecord(item)) throw new Error(`Phần tử tại /${index} không phải object.`);
    const id = idOf(item, shape.idKey, `/${index}`);
    if (byId.has(id)) {
      throw new Error(`Mã "${id}" xuất hiện hai lần — mã trùng thì không dựng cây được.`);
    }
    const rawParent = shape.parentKey in item ? item[shape.parentKey] : null;
    const parentId =
      typeof rawParent === "string" && rawParent !== ""
        ? rawParent
        : typeof rawParent === "number"
          ? String(rawParent)
          : null;
    const slot: Slot = { node: omit(item, shape.parentKey), id, parentId, children: [] };
    slots.push(slot);
    byId.set(id, slot);
  });

  const orphans: string[] = [];
  const cycles: string[] = [];
  const effectiveParent = new Map<Slot, Slot | null>();
  const state = new Map<Slot, "visiting" | "done">();

  const resolveParent = (slot: Slot): void => {
    if (state.get(slot) === "done") return;
    if (state.get(slot) === "visiting") {
      // Đi theo chuỗi parent mà quay lại chính mình → chu trình. Cắt tại đây.
      cycles.push(slot.id);
      effectiveParent.set(slot, null);
      state.set(slot, "done");
      return;
    }
    state.set(slot, "visiting");
    if (slot.parentId === null) {
      effectiveParent.set(slot, null);
    } else {
      const parent = byId.get(slot.parentId);
      if (parent === undefined) {
        orphans.push(slot.id);
        effectiveParent.set(slot, null);
      } else {
        resolveParent(parent);
        // Nếu chính slot này vừa bị cắt vì chu trình thì giữ nguyên quyết định cắt.
        if (!effectiveParent.has(slot)) effectiveParent.set(slot, parent);
      }
    }
    state.set(slot, "done");
  };

  for (const slot of slots) resolveParent(slot);

  // Gắn con theo thứ tự xuất hiện trong mảng đầu vào — giữ thứ tự văn bản.
  for (const slot of slots) {
    const parent = effectiveParent.get(slot) ?? null;
    if (parent !== null) parent.children.push(slot);
  }

  // Node lá không mang field con — round-trip với treeToFlat khớp từng byte.
  const build = (slot: Slot): JsonRecord =>
    slot.children.length === 0
      ? slot.node
      : { ...slot.node, [shape.childrenKey]: slot.children.map(build) };

  const roots = slots.filter((slot) => (effectiveParent.get(slot) ?? null) === null).map(build);

  return { roots, orphans, cycles };
}
