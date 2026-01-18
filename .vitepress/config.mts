import { defineConfig } from 'vitepress'
import fs from 'node:fs'
import path from 'node:path'
import { MermaidPlugin, MermaidMarkdown } from "vitepress-plugin-mermaid";

type SidebarItem = {
  text: string;
  link?: string;
  items?: SidebarItem[];
  collapsed?: boolean;
};

const llmDocsRoot = path.resolve(__dirname, '..', 'develop', 'llm');
const llmCategoryOrder = [
  'ai_integration',
  'design_standards',
  'messages',
  'platform_adapters',
  'plugin_system',
  'learning_system',
  'storage_utils',
  // legacy fallback
  'chunks',
] as const;

const llmCategoryLabels: Record<string, string> = {
  ai_integration: 'AI 集成',
  design_standards: '设计规范',
  messages: '消息',
  platform_adapters: '平台适配',
  plugin_system: '插件系统',
  learning_system: '学习系统',
  storage_utils: '存储与工具',
  chunks: 'Chunks（旧）',
};

function prettyName(stem: string): string {
  return stem
    .replace(/[-_]+/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function buildDirItems(
  dirAbs: string,
  linkPrefix: string,
  depth: number = 0,
  maxDepth: number = 2,
): SidebarItem[] {
  if (!fs.existsSync(dirAbs)) return [];

  const entries = fs.readdirSync(dirAbs, { withFileTypes: true });
  const files = entries
    .filter((e) => e.isFile() && e.name.endsWith('.md'))
    .map((e) => e.name)
    .sort((a, b) => a.localeCompare(b));
  const dirs = entries
    .filter((e) => e.isDirectory() && !e.name.startsWith('.'))
    .map((e) => e.name)
    .sort((a, b) => a.localeCompare(b));

  const items: SidebarItem[] = [];
  if (files.includes('index.md')) items.push({ text: '概览', link: `${linkPrefix}/` });

  for (const name of files) {
    if (name === 'index.md') continue;
    const stem = name.slice(0, -3);
    items.push({ text: prettyName(stem), link: `${linkPrefix}/${stem}` });
  }

  if (depth >= maxDepth) return items;

  for (const dir of dirs) {
    if (dir === 'snapshots') continue;
    const childAbs = path.join(dirAbs, dir);
    const childItems = buildDirItems(childAbs, `${linkPrefix}/${dir}`, depth + 1, maxDepth);
    if (!childItems.length) continue;

    const hasIndex = fs.existsSync(path.join(childAbs, 'index.md'));
    items.push({
      text: prettyName(dir),
      link: hasIndex ? `${linkPrefix}/${dir}/` : undefined,
      items: childItems,
      collapsed: true,
    });
  }

  return items;
}

function buildLlmSnapshotsSidebar(routeBase: string, fsBase: string): SidebarItem | null {
  const snapshotsDir = path.join(fsBase, 'snapshots');
  if (!fs.existsSync(snapshotsDir)) return null;

  const versions = fs
    .readdirSync(snapshotsDir, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort((a, b) => b.localeCompare(a));

  const versionItems: SidebarItem[] = [];
  for (const v of versions) {
    const vDir = path.join(snapshotsDir, v);
    const categoryDirs = fs
      .readdirSync(vDir, { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => e.name);

    const categories: SidebarItem[] = [];

    const orderedCats = llmCategoryOrder.filter((d) => categoryDirs.includes(d));
    const restCats = categoryDirs
      .filter((d) => d !== 'snapshots' && !orderedCats.includes(d as any))
      .sort((a, b) => a.localeCompare(b));

    for (const cat of [...orderedCats, ...restCats]) {
      if (cat === 'snapshots') continue;
      const catDir = path.join(vDir, cat);
      const prefix = `${routeBase}/snapshots/${v}/${cat}`;
      const links = buildDirItems(catDir, prefix);
      if (links.length) {
        categories.push({ text: llmCategoryLabels[cat] || prettyName(cat), items: links, collapsed: true });
      }
    }

    versionItems.push({
      text: v,
      link: `${routeBase}/snapshots/${v}/`,
      items: categories,
      collapsed: true,
    });
  }

  return {
    text: '快照',
    link: `${routeBase}/snapshots/`,
    items: versionItems,
    collapsed: true,
  };
}

function buildLlmSidebar(routeBase: string, fsBase: string): SidebarItem[] {
  const groups: SidebarItem[] = [{ text: '概览', link: `${routeBase}/` }];

  if (!fs.existsSync(fsBase)) return groups;

  const topDirs = fs
    .readdirSync(fsBase, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name);

  const ordered = llmCategoryOrder.filter((d) => topDirs.includes(d));
  const rest = topDirs
    .filter((d) => d !== 'snapshots' && !ordered.includes(d as any))
    .sort((a, b) => a.localeCompare(b));

  for (const dir of [...ordered, ...rest]) {
    if (dir === 'snapshots') continue;
    const dirAbs = path.join(fsBase, dir);
    const links = buildDirItems(dirAbs, `${routeBase}/${dir}`);
    if (!links.length) continue;
    groups.push({ text: llmCategoryLabels[dir] || prettyName(dir), items: links, collapsed: true });
  }

  const snapshots = buildLlmSnapshotsSidebar(routeBase, fsBase);
  if (snapshots) groups.push(snapshots);

  return groups;
}

const routes = {
  maibotMain: '/develop/llm/maibot/main',
  maibotDev: '/develop/llm/maibot/dev',
  maimMessageMaster: '/develop/llm/maim_message/master',
} as const;

const fsRoots = {
  maibotMain: path.join(llmDocsRoot, 'maibot', 'main'),
  maibotDev: path.join(llmDocsRoot, 'maibot', 'dev'),
  maimMessageMaster: path.join(llmDocsRoot, 'maim_message', 'master'),
} as const;

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "MaiBot 文档中心",
  description: "MaiBot / maim_message 自动化维护的开发文档（按仓库与分支隔离）",
  base: process.env.VITEPRESS_BASE || "/",
  head: [
    ['link', { rel: 'icon', href: '/title_img/mai2.png' }]
  ],
  themeConfig: {
    search: {
      provider: 'local',
    },
    editLink: {
      pattern: "https://github.com/Mai-with-u/docs/edit/main/:path",
      text: "文档有误？在 GitHub 上编辑此页"
    },
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: 'MaiBot（main）', link: `${routes.maibotMain}/` },
      { text: 'MaiBot（dev）', link: `${routes.maibotDev}/` },
      { text: 'maim_message（master）', link: `${routes.maimMessageMaster}/` },
      {
        text: 'GitHub', 
        items: [
          { text: 'MaiBot', link: 'https://github.com/Mai-with-u/MaiBot' },
          { text: 'maim_message', link: 'https://github.com/Mai-with-u/maim_message' },
          { text: 'MaiBot Docs', link: 'https://github.com/Mai-with-u/docs' },
        ]
      },
    ],
    outline: [1, 4],
    sidebar: {
      [`${routes.maibotMain}/`]: buildLlmSidebar(routes.maibotMain, fsRoots.maibotMain),
      [`${routes.maibotDev}/`]: buildLlmSidebar(routes.maibotDev, fsRoots.maibotDev),
      [`${routes.maimMessageMaster}/`]: buildLlmSidebar(routes.maimMessageMaster, fsRoots.maimMessageMaster),
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Mai-with-u/MaiBot' }
    ],

    lastUpdated: {
      text: "最后更新",
      formatOptions: {
        dateStyle: "short",
        timeStyle: "short",
      },
    },
  },
  markdown: {
    config(md) {
      md.use(MermaidMarkdown);
    },
  },
  vite: {
    plugins: [MermaidPlugin()],
    optimizeDeps: {
      include: ['mermaid'],
    },
    ssr: {
      noExternal: ['mermaid'],
    },
  },
})
