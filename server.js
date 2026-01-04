import express from "express";
import { execFile } from "child_process";
import fs from "fs/promises";
import path from "path";
import os from "os";

const app = express();
app.use(express.json({ limit: "10mb" }));

app.get("/health", (_, res) => res.json({ ok: true }));

app.post("/convert", async (req, res) => {
  const { content = "", from = "markdown", to = "pdf" } = req.body ?? {};
  if (!content) return res.status(400).json({ error: "content is required" });

  // 临时目录
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), "pandoc-"));
  const inFile = path.join(dir, `input.${from === "markdown" ? "md" : "txt"}`);
  const outFile = path.join(dir, `output.${to}`);

  try {
    await fs.writeFile(inFile, content, "utf8");

    // 说明：生成 PDF 默认依赖 LaTeX（此镜像已带 TeX Live）
    const args = [inFile, "-f", from, "-t", to, "-o", outFile];

    execFile("pandoc", args, async (err, _stdout, stderr) => {
      if (err) {
        return res.status(500).json({ error: "pandoc failed", detail: stderr || err.message });
      }

      const buf = await fs.readFile(outFile);

      // 简单设置 Content-Type
      const ct =
        to === "pdf" ? "application/pdf" :
        to === "docx" ? "application/vnd.openxmlformats-officedocument.wordprocessingml.document" :
        "application/octet-stream";

      res.setHeader("Content-Type", ct);
      res.setHeader("Content-Disposition", `attachment; filename="output.${to}"`);
      res.send(buf);
    });
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

const PORT = process.env.PORT || 3000;
// 关键：要监听 0.0.0.0，容器外才能访问
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Pandoc API listening on ${PORT}`);
});
