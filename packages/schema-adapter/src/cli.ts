/**
 * CLI của @sankit/schema-adapter.
 *
 *   pnpm --filter @sankit/schema-adapter cli -- lint <schema.json>
 *   pnpm --filter @sankit/schema-adapter cli -- validate --schema <schema.json> <file-hoặc-thư-mục...>
 *
 * Exit code: 0 sạch, 1 có lỗi, 2 dùng sai lệnh — cắm vào CI được.
 */

import { readFile, readdir, stat } from "node:fs/promises";
import { basename, join, resolve } from "node:path";
import { parseArgs } from "node:util";

import { lintSchema } from "./lint.ts";
import { isRecord, type JsonValue } from "./types.ts";
import { validateAgainstSchema } from "./validate.ts";

async function loadJson(path: string): Promise<JsonValue> {
  return JSON.parse(await readFile(resolve(path), "utf8")) as JsonValue;
}

/** Một file .json, hoặc thư mục chứa nhiều file .json. */
async function collectJsonFiles(target: string): Promise<string[]> {
  const path = resolve(target);
  const info = await stat(path);
  if (info.isFile()) return [path];
  const entries = (await readdir(path)).filter((name) => name.endsWith(".json")).sort();
  return entries.map((entry) => join(path, entry));
}

async function runLint(args: string[]): Promise<number> {
  const target = args[0];
  if (target === undefined) {
    process.stderr.write("Cách dùng: lint <schema.json>\n");
    return 2;
  }
  const schema = await loadJson(target);
  if (!isRecord(schema)) {
    process.stderr.write("File schema phải là một object JSON.\n");
    return 2;
  }

  const report = lintSchema(schema);
  for (const finding of report.findings) {
    const tag = finding.level === "error" ? "LỖI     " : "CẢNH BÁO";
    process.stdout.write(`${tag} ${finding.path}\n         [${finding.rule}] ${finding.message}\n`);
  }
  const errors = report.findings.filter((finding) => finding.level === "error").length;
  const warnings = report.findings.length - errors;
  process.stdout.write(
    report.ok
      ? `\nSchema dùng được với structured outputs (${warnings} cảnh báo).\n`
      : `\nSchema CHƯA dùng được: ${errors} lỗi, ${warnings} cảnh báo.\n`,
  );
  return report.ok ? 0 : 1;
}

async function runValidate(args: string[]): Promise<number> {
  const { values, positionals } = parseArgs({
    args,
    options: { schema: { type: "string" } },
    allowPositionals: true,
  });
  if (values.schema === undefined || positionals.length === 0) {
    process.stderr.write("Cách dùng: validate --schema <schema.json> <file-hoặc-thư-mục...>\n");
    return 2;
  }
  const schema = await loadJson(values.schema);
  if (!isRecord(schema)) {
    process.stderr.write("File schema phải là một object JSON.\n");
    return 2;
  }

  const files = (await Promise.all(positionals.map(collectJsonFiles))).flat();
  if (files.length === 0) {
    process.stderr.write("Không tìm thấy file .json nào để kiểm.\n");
    return 2;
  }

  let failed = 0;
  for (const file of files) {
    const issues = validateAgainstSchema(await loadJson(file), schema);
    if (issues.length === 0) {
      process.stdout.write(`OK   ${basename(file)}\n`);
    } else {
      failed += 1;
      process.stdout.write(`FAIL ${basename(file)} — ${issues.length} lỗi\n`);
      for (const issue of issues) {
        process.stdout.write(`     ${issue.path === "" ? "/" : issue.path}: ${issue.message}\n`);
      }
    }
  }
  process.stdout.write(`\n${files.length - failed}/${files.length} file đúng schema.\n`);
  return failed === 0 ? 0 : 1;
}

export async function run(argv: readonly string[]): Promise<number> {
  // `pnpm run <script> -- lint ...` truyền luôn dấu `--` vào argv của script.
  const args = [...argv];
  if (args[0] === "--") args.shift();
  const command = args.shift();

  if (command === "lint") return runLint(args);
  if (command === "validate") return runValidate(args);

  process.stderr.write(
    "Cách dùng:\n  lint <schema.json>\n  validate --schema <schema.json> <file-hoặc-thư-mục...>\n",
  );
  return 2;
}

const isDirectRun =
  process.argv[1] !== undefined && import.meta.url.endsWith(basename(process.argv[1]));
if (isDirectRun) {
  process.exitCode = await run(process.argv.slice(2));
}
