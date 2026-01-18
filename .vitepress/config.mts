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

function prettyName(stem: string): string {
  return stem
    .replace(/[-_]+/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function listMarkdownLinks(dirAbs: string, linkPrefix: string): SidebarItem[] {
  if (!fs.existsSync(dirAbs)) return [];
  const entries = fs.readdirSync(dirAbs, { withFileTypes: true });
  const files = entries
    .filter((e) => e.isFile() && e.name.endsWith('.md'))
    .map((e) => e.name)
    .sort((a, b) => a.localeCompare(b));

  const items: SidebarItem[] = [];
  if (files.includes('index.md')) items.push({ text: '概览', link: `${linkPrefix}/` });

  for (const name of files) {
    if (name === 'index.md') continue;
    const stem = name.slice(0, -3);
    items.push({ text: prettyName(stem), link: `${linkPrefix}/${stem}` });
  }

  return items;
}

function buildLlmSnapshotsSidebar(branch: 'main' | 'dev'): SidebarItem | null {
  if (branch !== 'main') return null;

  const branchRoot = path.join(llmDocsRoot, branch);
  const snapshotsDir = path.join(branchRoot, 'snapshots');
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
      .map((e) => e.name)
      .sort((a, b) => a.localeCompare(b));

    const categories: SidebarItem[] = [];
    for (const cat of categoryDirs) {
      if (cat === 'snapshots') continue;
      const catDir = path.join(vDir, cat);
      const prefix = `/develop/llm/${branch}/snapshots/${v}/${cat}`;
      const links = listMarkdownLinks(catDir, prefix);
      if (links.length) {
        categories.push({ text: prettyName(cat), items: links, collapsed: true });
      }
    }

    versionItems.push({
      text: v,
      link: `/develop/llm/${branch}/snapshots/${v}/`,
      items: categories,
      collapsed: true,
    });
  }

  return {
    text: '快照',
    link: `/develop/llm/${branch}/snapshots/`,
    items: versionItems,
    collapsed: true,
  };
}

function buildLlmSidebar(branch: 'main' | 'dev'): SidebarItem[] {
  const branchRoot = path.join(llmDocsRoot, branch);
  const groups: SidebarItem[] = [{ text: '概览', link: `/develop/llm/${branch}/` }];

  if (!fs.existsSync(branchRoot)) return groups;

  const topDirs = fs
    .readdirSync(branchRoot, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort((a, b) => a.localeCompare(b));

  for (const dir of topDirs) {
    if (dir === 'snapshots') continue;
    const dirAbs = path.join(branchRoot, dir);
    const links = listMarkdownLinks(dirAbs, `/develop/llm/${branch}/${dir}`);
    if (!links.length) continue;
    groups.push({ text: prettyName(dir), items: links, collapsed: false });
  }

  const snapshots = buildLlmSnapshotsSidebar(branch);
  if (snapshots) groups.push(snapshots);

  return groups;
}

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "MaiBot 文档中心",
  description: "MaiBot 开发与使用的全方位指南",
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
      { text: '功能介绍',link: '/features/index'},
      { text: '用户手册', link: '/manual/' },
      { text: '开发文档', link: '/develop/' },
      { text: '开发文档(main)', link: '/develop/llm/main/' },
      { text: '开发文档(dev)', link: '/develop/llm/dev/' },
      {text: '官方Q群', link:'/manual/other/qq_group'},
      {
        text: 'GitHub', 
        items: [
          { text: 'MaiBot', link: 'https://github.com/Mai-with-u/MaiBot' },
          { text: 'MaiBot Docs', link: 'https://github.com/Mai-with-u/docs' },
        ]
      },
    ],
    outline: [1, 4],
    sidebar: {
      '/manual/': [
        {
          text: '安装方法',
          collapsed: false,
          items: [
            { text: '部署概览', link: '/manual/deployment/' },
            { text: 'Windows部署', link: '/manual/deployment/mmc_deploy_windows' },
            { text: 'Linux部署', link: '/manual/deployment/mmc_deploy_linux' },
            { text: 'macOS部署', link: '/manual/deployment/mmc_deploy_macos' },
            { text: 'Docker部署', link: '/manual/deployment/mmc_deploy_docker' },
            { text: '其他部署方式', 
              collapsed: true, 
              items: [
                { text: 'Android部署', link: '/manual/deployment/mmc_deploy_android' },
                { text: 'Kubernetes部署', link: '/manual/deployment/mmc_deploy_kubernetes' },
                { text: '1Panel 部署(社区)', link: '/manual/deployment/community/1panel' },
                { text: 'Linux一键部署(社区)', link: '/manual/deployment/community/linux_one_key' },
              ],
            },
          ]
        },
        {
          text: '配置详解',
          collapsed: false,
          items: [
            { text: '配置概览', link: '/manual/configuration/' },
            { text: '关于配置指南', link: '/manual/configuration/configuration_standard' },
            { text: '关于模型配置', link: '/manual/configuration/configuration_model_standard' },
            { text: 'WebUI配置指南', link: '/manual/configuration/config_windows_onekey_withwebui'},
            { text: '关于LPMM', 
              collapsed: true, 
              items: [
                { text: '使用说明', link: '/manual/configuration/lpmm/lpmm' },
                { text: '手动编译说明', link: '/manual/configuration/lpmm/lpmm_compile_and_install'},
                { text: '导入文件格式', link: '/manual/configuration/lpmm/lpmm_knowledge_template' },
              ]
            },
            { text: '关于备份', link: '/manual/configuration/backup' },
          ]
        },
        {
          text: '适配器列表',
          collapsed: false,
          items: [
            { text: 'Adapters 文档中心', link: '/manual/adapters' },
            { text: 'MaiBot Napcat Adapter', link: '/manual/adapters/napcat' },
            { text: 'GO-CQ Adapter', link: '/manual/adapters/gocq' },
            {
              text: 'MaiBot TTS Adapter', 
              collapsed: true, 
              items: [
                { text: '基本介绍', link: '/manual/adapters/tts/' },
                { text: 'GPT_Sovits TTS', link: '/manual/adapters/tts/gpt_sovits' },
                { text: '豆包 TTS', link: '/manual/adapters/tts/doubao_tts' },
                { text: '千问Omni TTS', link: '/manual/adapters/tts/qwen_omni' },
              ]
            },
          ]
        },
        {
          text: '常见问题',
          collapsed: false,
          items: [
            { text: 'FAQ 概览', link: '/manual/faq/' },
          ]
        },
        {
          text: '参考资源',
          collapsed: false,
          items: [
            { text: '如何高效提问', link: '/manual/other/smart-question-guide' },
            { text: '官方Q群', link: '/manual/other/qq_group' },
            { text: '最终用户许可协议', link: '/manual/other/EULA' },
          ]
        },
        { text: '更新日志', link: '/manual/other/changelog' },
      ],
 
      '/develop/': [
        {
          text: '开发文档',
          items: [
            { text: '介绍', link: '/develop/' },
            { text: '开发者与代码规范', link: '/develop/develop_standard' },
          ]
        },
        {
          text: '适配器开发',
          collapsed: false,
          items: [
            { text: '开发综述', link: '/develop/adapter_develop/' },
            { text: 'Adapter 开发指南', link: '/develop/adapter_develop/develop_adapter' },
          ]
        },
        {
          text: '插件开发',
          collapsed: false,
          items: [
            { text: '开发指南', link: '/develop/plugin_develop/' },
            { text: '快速开始', link: '/develop/plugin_develop/quick-start'},
            { text: 'Manifest系统指南', link: '/develop/plugin_develop/manifest-guide' },
            { text: 'Actions系统', link: '/develop/plugin_develop/action-components' },
            { text: '命令处理系统', link: '/develop/plugin_develop/command-components' },
            { text: '工具系统', link: '/develop/plugin_develop/tool-components' },
            { text: '配置管理指南', link: '/develop/plugin_develop/configuration-guide' },
            { text: '依赖管理', link: '/develop/plugin_develop/dependency-management' },
            { text: 'WebUI集成', link: '/develop/plugin_develop/plugin-config-schema' },
            { text: 'API参考',
              collapsed: true,
              items: [
                { text: '发送API', link: '/develop/plugin_develop/api/send-api' },
                { text: '消息API', link: '/develop/plugin_develop/api/message-api' },
                { text: '聊天流API', link: '/develop/plugin_develop/api/chat-api' },
                { text: 'LLM API', link: '/develop/plugin_develop/api/llm-api' },
                { text: '回复生成器API', link: '/develop/plugin_develop/api/generator-api' },
                { text: '表情包API', link: '/develop/plugin_develop/api/emoji-api' },
                { text: '人物信息API', link: '/develop/plugin_develop/api/person-api' },
                { text: '数据库API', link: '/develop/plugin_develop/api/database-api' },
                { text: '配置API', link: '/develop/plugin_develop/api/config-api' },
                { text: '插件API', link: '/develop/plugin_develop/api/plugin-manage-api' },
                { text: '组件API', link: '/develop/plugin_develop/api/component-manage-api' },
                { text: '日志API', link: '/develop/plugin_develop/api/logging-api' },
                { text: '工具API', link: '/develop/plugin_develop/api/tool-api'}
              ]
            },

          ]
        },
        {
          text: 'Maim_Message参考',
          collapsed: false,
          items: [
            { text: 'Maim_Message 概述', link: '/develop/maim_message/' },
            { text: 'Message_Base', link: '/develop/maim_message/message_base' },
            { text: 'Router', link: '/develop/maim_message/router' },
            { text: '命令参数表', link: '/develop/maim_message/command_args'}
          ]
        }
      ],
      '/develop/llm/main/': buildLlmSidebar('main'),
      '/develop/llm/dev/': buildLlmSidebar('dev'),
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
