# theme.py
THEME_COLORS = {
    'light': {
        'bg_main': "#F8F9FA",
        'bg_card': "#FFFFFF",
        'fg_main': "#212529",
        'fg_sub': "#6C757D",
        'border': "#DEE2E6",
        'entry_bg': "#FFFFFF",
        'entry_fg': "#212529",
        'entry_border': "#CED4DA",
        'tree_heading': "#E9ECEF",
        'primary': "#0D6EFD",
        'primary_hover': "#0B5ED7",
        'success': "#198754",
        'success_hover': "#157347",
        'accent': "#6F42C1",
        'accent_hover': "#59359A"
    },
    'dark': {
        'bg_main': "#1A1B26",
        'bg_card': "#24283B",
        'fg_main': "#C0CAF5",
        'fg_sub': "#7A8299",
        'border': "#3B4261",
        'entry_bg': "#2A2E42",
        'entry_fg': "#C0CAF5",
        'entry_border': "#3B4261",
        'tree_heading': "#2D334F",
        
        'primary': "#4B6EFF",
        'primary_hover': "#5F7EFF",
        'success': "#41A858",
        'success_hover': "#4ECB6A",
        'accent': "#9D7CD8",
        'accent_hover': "#B492E8"
    }
}

class ThemeManager:
    """主题管理器"""
    def __init__(self, root, style):
        self.root = root
        self.style = style
        self.current_theme = 'light'
        
        self._configure_styles()
    
    def _configure_styles(self):
        """配置基础ttk样式"""
        font_family = "Microsoft YaHei"
        font_size = 10
        
        self.style.configure("TCombobox", 
                           borderwidth=1, relief="solid",
                           font=(font_family, font_size))
        self.style.configure("TNotebook", borderwidth=0)
        self.style.configure("TNotebook.Tab", 
                           borderwidth=1,
                           font=(font_family, font_size))
    
    def apply_theme(self, theme: str):
        """应用主题到所有组件"""
        self.current_theme = theme
        colors = THEME_COLORS[theme]
        font_family = "Microsoft YaHei"
        font_size = 10
        
        self.root.configure(bg=colors['bg_main'])
        
        # ===== Notebook - 去除边框和背景色 =====
        self.style.configure("TNotebook", 
                           background=colors['bg_main'], 
                           borderwidth=0,
                           highlightthickness=0)
        
        # ===== Notebook.Tab - 让标签背景和主背景一致，去除边框线 =====
        self.style.configure("TNotebook.Tab", 
                           background=colors['tree_heading'],
                           foreground=colors['fg_main'],
                           borderwidth=0,
                           padding=[12, 4],
                           font=(font_family, font_size))
        self.style.map("TNotebook.Tab",
                      background=[("selected", colors['bg_card'])],
                      foreground=[("selected", colors['primary'])],
                      expand=[("selected", [0, 0, 0, 0])])
        
        # 关键：让 Notebook 的 client 区域背景色和主背景一致
        self.style.map("TNotebook",
                      background=[('', colors['bg_main'])])
        
        # Treeview
        self.style.configure("Treeview",
                           background=colors['bg_card'],
                           fieldbackground=colors['bg_card'],
                           foreground=colors['fg_main'],
                           borderwidth=0,
                           rowheight=26,
                           font=(font_family, font_size))
        self.style.configure("Treeview.Heading",
                           background=colors['tree_heading'],
                           foreground=colors['fg_main'],
                           borderwidth=1,
                           borderColor=colors['border'],
                           font=(font_family, font_size, "bold"))
        self.style.map("Treeview",
                      background=[('selected', colors['primary'])],
                      foreground=[('selected', 'white')])
        
        # Combobox
        entry_border = colors.get('entry_border', colors['border'])
        self.style.configure("TCombobox",
                           fieldbackground=colors['entry_bg'],
                           background=colors['entry_bg'],
                           foreground=colors['entry_fg'],
                           arrowcolor=colors['fg_main'],
                           bordercolor=entry_border,
                           lightcolor=entry_border,
                           darkcolor=entry_border,
                           borderwidth=1,
                           relief="solid",
                           font=(font_family, font_size))
        self.style.map("TCombobox",
                      fieldbackground=[('readonly', colors['entry_bg'])],
                      background=[('readonly', colors['entry_bg'])],
                      foreground=[('readonly', colors['entry_fg'])])
        
        # Progressbar
        self.style.configure("TProgressbar",
                           background=colors['primary'],
                           troughcolor=colors['tree_heading'],
                           bordercolor=colors['border'],
                           lightcolor=colors['border'],
                           darkcolor=colors['border'])
        
        # Scrollbar
        self.style.configure("TScrollbar",
                           background=colors['tree_heading'],
                           troughcolor=colors['bg_main'],
                           bordercolor=colors['border'],
                           arrowcolor=colors['fg_main'])
        
        # Labelframe
        self.style.configure("TLabelframe",
                           background=colors['bg_main'],
                           foreground=colors['fg_main'],
                           bordercolor=colors['border'])
        self.style.configure("TLabelframe.Label",
                           font=(font_family, font_size, "bold"))
        
        return colors