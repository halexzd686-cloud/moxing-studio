/**
 * moxing-studio themes — v1.0
 * 每套主题 = 固定角色集合。生成图表时内联其中一套，禁止跨主题取色。
 * 角色契约：
 *   BG/TXT/MUT/GRID  环境四件
 *   DATA/RAMP        有序与单序列数据（RAMP 按重要性分配，最深 = 主角）
 *   CAT              无序类目，硬上限 4；超过 4 类必须降级用 RAMP
 *   HERO             全图唯一强调色，只允许一个主角
 *   DARK             暗底标记，驱动线宽与明度校验（暗底线宽已直接并入）
 */

const THEMES = {

  paper: {  // 白纸 · 默认 · 日常组会
    DARK: false,
    BG: "#FAFAF7", TXT: "#23262B", MUT: "#8A8F98", GRID: "#E4E3DE",
    DATA: "#2F6B4F",
    RAMP: ["#2F6B4F", "#5E9478", "#93BCA4", "#C5DBCF"],
    CAT:  ["#2F6B4F", "#C46A4A", "#4A6FA5", "#D9A441"],
    HERO: "#C46A4A",
    FONT: "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
    LINE_WIDTH: 2, RADIUS: 12
  },

  ink: {  // 墨 · 侘寂基底 + 一味朱砂（小圆角，近碑刻感）
    DARK: false,
    BG: "#F4F1EA", TXT: "#1F1D1A", MUT: "#7D786C", GRID: "#E0DCD2",
    DATA: "#1F1D1A",
    RAMP: ["#1F1D1A", "#4A463E", "#7D786C", "#B5B0A4"],
    CAT:  ["#1F1D1A", "#9A3B2E", "#6B7F5E", "#B08A3E"],
    HERO: "#9A3B2E",
    FONT: "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
    LINE_WIDTH: 2, RADIUS: 4
  },

  boardroom: {  // 董事会 · 正式汇报默认项
    DARK: false,
    BG: "#FBFAF7", TXT: "#1B2331", MUT: "#7A8291", GRID: "#E5E4DF",
    DATA: "#1E3A5F",
    RAMP: ["#1E3A5F", "#3D5D85", "#6E89AC", "#A8BACF"],
    CAT:  ["#1E3A5F", "#B08D3E", "#7C93A8", "#8C5A4A"],
    HERO: "#B08D3E",
    FONT: "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
    LINE_WIDTH: 2, RADIUS: 8
  },

  tech: {  // 深色科技 · 屏幕共享特化（线宽已 ×1.5 并入）
    DARK: true,
    BG: "#16181D", TXT: "#E8EAF0", MUT: "#8B91A0", GRID: "#2A2E38",
    DATA: "#5B8DEF",
    RAMP: ["#5B8DEF", "#7FA5F2", "#A3BDF6", "#C7D6FA"],
    CAT:  ["#5B8DEF", "#4ECBA8", "#F0A35E", "#E07A8B"],
    HERO: "#F0A35E",
    FONT: "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
    LINE_WIDTH: 3, RADIUS: 12
  },

  mori: {  // 山野 · 莫兰迪 · HR/ESG/文化
    DARK: false,
    BG: "#F5F4EF", TXT: "#3A3D38", MUT: "#8F8C82", GRID: "#E4E2D8",
    DATA: "#7D8F69",
    RAMP: ["#7D8F69", "#9BAE8A", "#BAC7AD", "#D7DFCE"],
    CAT:  ["#7D8F69", "#C4A484", "#A67B7B", "#8A9BA8"],
    HERO: "#B5724A",
    FONT: "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
    LINE_WIDTH: 2, RADIUS: 12
  },

  dawn: {  // 破晓 · 发布会/晚宴（HERO 用亮色，暗底强调反转为最亮）
    DARK: true,
    BG: "#1C1B22", TXT: "#F0EDEA", MUT: "#98949E", GRID: "#2E2C36",
    DATA: "#D4A24E",
    RAMP: ["#D4A24E", "#DFB876", "#EACD9E", "#F3E2C6"],
    CAT:  ["#D4A24E", "#8FA3BF", "#B0708C", "#7BA88F"],
    HERO: "#E8E4DE",
    FONT: "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif",
    LINE_WIDTH: 3, RADIUS: 12
  }
};
