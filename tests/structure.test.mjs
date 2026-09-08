import assert from "node:assert/strict";
import { access, readFile, readdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { extname, join, relative } from "node:path";
import test from "node:test";

const root = fileURLToPath(new URL("..", import.meta.url));
const expected = {
  "name": "google-cloud",
  "version": "0.2.10",
  "url": "https://github.com/PedroAVJ/google-cloud",
  "dependencies": []
};

async function json(...parts) {
  return JSON.parse(await readFile(join(root, ...parts), "utf8"));
}

async function textFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  const textExtensions = new Set([".json", ".js", ".md", ".mjs", ".sh", ".toml", ".yaml", ".yml"]);

  for (const entry of entries) {
    if (entry.name === ".git" || entry.name === "node_modules") continue;
    const path = join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...await textFiles(path));
    } else if (textExtensions.has(extname(entry.name))) {
      files.push(path);
    }
  }

  return files;
}

test("standalone plugin metadata is synchronized", async () => {
  const codex = await json(".codex-plugin", "plugin.json");
  assert.equal(codex.name, expected.name);
  assert.equal(codex.version, expected.version);
  assert.equal(codex.homepage, expected.url);
  assert.equal(codex.repository, expected.url);
  await access(join(root, "README.md"));
  await access(join(root, "AGENTS.md"));
  await access(join(root, "account", "README.md"));

  if (expected.codexOnly) {
    await assert.rejects(access(join(root, ".claude-plugin", "plugin.json")));
  } else {
    const claude = await json(".claude-plugin", "plugin.json");
    assert.equal(claude.name, codex.name);
    assert.equal(claude.version, codex.version);
    assert.equal(claude.homepage, expected.url);
    assert.equal(claude.repository, expected.url);
    for (const dependency of expected.dependencies) {
      assert.ok((claude.dependencies ?? []).includes(dependency));
    }
  }

  const pkg = await json("package.json");
  assert.equal(pkg.version, expected.version);
  assert.equal(pkg.homepage, expected.url + "#readme");
  assert.equal(pkg.repository.url, "git+" + expected.url + ".git");
  assert.equal(pkg.bin, undefined);
  assert.equal(pkg.dependencies, undefined);
});

test("publishing is skill-only and uses native gcloud storage", async () => {
  await assert.rejects(access(join(root, "bin")));

  const publish = await readFile(join(root, "skills", "publish", "SKILL.md"), "utf8");
  assert.match(publish, /gcloud auth list/);
  assert.match(publish, /gcloud projects list/);
  assert.match(publish, /gcloud storage ls/);
  assert.match(publish, /gcloud storage cp/);
  assert.match(publish, /--no-clobber/);
  assert.match(publish, /Google Drive/);
  assert.doesNotMatch(publish, /application-default/);

  const retiredCommand = ["publish", "file"].join("-");
  const retiredConfigDirectory = [".", retiredCommand].join("");
  const retiredLibrary = ["@google-cloud", "storage"].join("/");
  const forbidden = [
    retiredCommand,
    retiredConfigDirectory,
    retiredLibrary,
    ["com", "mander"].join(""),
    ["GCP", "PROJECT", "ID"].join("_"),
    ["GCS", "PUBLIC", "BUCKET"].join("_"),
    ["GCS", "PRIVATE", "BUCKET"].join("_"),
  ];

  for (const path of await textFiles(root)) {
    const contents = await readFile(path, "utf8");
    for (const value of forbidden) {
      assert.equal(contents.includes(value), false, `${relative(root, path)} still references retired wrapper state`);
    }
  }
});

test("operator account maps stay outside the distributable plugin", async () => {
  const readme = await readFile(join(root, "README.md"), "utf8");
  const skill = await readFile(join(root, "skills", "google-cloud", "SKILL.md"), "utf8");
  const account = await readFile(join(root, "account", "README.md"), "utf8");
  assert.match(readme, /account\/README\.md/);
  assert.match(skill, /GOOGLE_CLOUD_INFRASTRUCTURE_FILE/);
  assert.match(account, /~\/\.config\/google-cloud-plugin\/infrastructure\.md/);
  assert.match(account, /map never authorizes/);
  await assert.rejects(access(join(root, "account", "infrastructure.md")));
});
