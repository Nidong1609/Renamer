import tkinter as tk
from tkinter import ttk, filedialog
import os
from language import LANG_DICT
from theme import THEME_COLORS, ThemeManager

# ============ 全局字体配置 ============
FONT_FAMILY = "Microsoft YaHei"
FONT_SIZE_NORMAL = 10
FONT_SIZE_BOLD = 10
FONT_SIZE_SMALL = 9
FONT_SIZE_LARGE = 11

# ============ 统一尺寸常量 ============
ENTRY_WIDTH_SMALL = 7    # 数字输入框
ENTRY_WIDTH_MEDIUM = 20  # 前缀输入框
ENTRY_WIDTH_LARGE = 30   # 扩展名/查找替换输入框
SPACING_SMALL = 5
SPACING_MEDIUM = 8
SPACING_LARGE = 12
ROW_PADDING = 5


class TopBar(tk.Frame):
    """顶部控制栏（语言、主题切换）"""
    def __init__(self, master, on_lang_change, on_theme_change, **kwargs):
        super().__init__(master, **kwargs)
        self.on_lang_change = on_lang_change
        self.on_theme_change = on_theme_change
        # 语言下拉框的选项直接来自 LANG_DICT 的 key，
        # 以后 language.py 里加多少种语言都不用再改这里
        self.lang_codes = list(LANG_DICT.keys())
        self.current_theme_code = 'light'
        
        self._create_widgets()
    
    def _create_widgets(self):
        self.columnconfigure(2, weight=1)
        
        self.lbl_lang = tk.Label(self, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_lang.grid(row=0, column=0, padx=(0, SPACING_SMALL), sticky='e')
        
        lang_names = [LANG_DICT[code].get('lang_name', code) for code in self.lang_codes]
        self.lang_combo = ttk.Combobox(
            self, values=lang_names, 
            state="readonly", width=8, font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        self.lang_combo.grid(row=0, column=1, padx=(0, SPACING_LARGE * 2), sticky='w')
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_lang_select)
        
        self.lbl_theme = tk.Label(self, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_theme.grid(row=0, column=3, padx=(0, SPACING_SMALL), sticky='e')
        
        self.theme_combo = ttk.Combobox(
            self, values=["Light", "Dark"], 
            state="readonly", width=8, font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        self.theme_combo.grid(row=0, column=4, sticky='w')
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_select)
    
    def _on_lang_select(self, event=None):
        """按下拉列表里的位置换算回语言代码，不再用具体文字（"中文"/"English"）猜语言，
        这样以后加第三、第四种语言也不用改这里"""
        idx = self.lang_combo.current()
        if 0 <= idx < len(self.lang_codes):
            self.on_lang_change(self.lang_codes[idx])
    
    def _on_theme_select(self, event=None):
        """主题下拉框永远是 [浅色项, 深色项] 这个顺序，用位置索引判断，
        不管当前显示的文字是哪种语言"""
        idx = self.theme_combo.current()
        self.current_theme_code = 'dark' if idx == 1 else 'light'
        self.on_theme_change(self.current_theme_code)
    
    def set_theme_code(self, theme_code: str):
        """供外部（比如加载配置文件时）直接设置当前主题代码，不触发回调"""
        self.current_theme_code = theme_code
    
    def set_language(self, lang_code: str, lang_dict: dict):
        self.lbl_lang.config(text=lang_dict['lbl_lang'])
        self.lbl_theme.config(text=lang_dict['lbl_theme'])
        
        idx = self.lang_codes.index(lang_code) if lang_code in self.lang_codes else 0
        self.lang_combo.current(idx)
        
        # 用 current_theme_code（light/dark）而不是旧的显示文字来决定选中项，
        # 这样切换语言时下拉列表候选文字和当前选中项都会正确本地化
        self.theme_combo.config(values=[lang_dict['theme_light'], lang_dict['theme_dark']])
        self.theme_combo.current(1 if self.current_theme_code == 'dark' else 0)
    
    def apply_theme(self, colors: dict):
        self.configure(bg=colors['bg_main'])
        self.lbl_lang.config(bg=colors['bg_main'], fg=colors['fg_main'])
        self.lbl_theme.config(bg=colors['bg_main'], fg=colors['fg_main'])


class DirSelector(tk.Frame):
    """目录选择器"""
    def __init__(self, master, on_select, **kwargs):
        super().__init__(master, **kwargs)
        self.on_select = on_select
        self.dir_path = tk.StringVar()
        self._create_widgets()
    
    def _create_widgets(self):
        self.columnconfigure(1, weight=1)
        
        self.lbl_dir = tk.Label(self, font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        self.lbl_dir.grid(row=0, column=0, sticky='w', padx=(0, SPACING_LARGE))
        
        self.entry_dir = tk.Entry(
            self, textvariable=self.dir_path, 
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), relief="solid", bd=1
        )
        self.entry_dir.grid(row=0, column=1, sticky='ew', padx=SPACING_SMALL)
        
        self.btn_browse = tk.Button(
            self, text="浏览...", command=self._browse,
            font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"), relief="flat", 
            bd=0, cursor="hand2", padx=18, pady=5, width=6
        )
        self.btn_browse.grid(row=0, column=2, padx=(SPACING_SMALL, 0))
    
    def _browse(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_path.set(path)
            self.on_select(path)
    
    def get_path(self) -> str:
        return self.dir_path.get()
    
    def set_path(self, path: str):
        self.dir_path.set(path)
    
    def set_language(self, lang_dict: dict):
        self.lbl_dir.config(text=lang_dict['lbl_dir'])
        self.btn_browse.config(text=lang_dict['btn_browse'])
    
    def apply_theme(self, colors: dict):
        self.configure(bg=colors['bg_main'])
        self.lbl_dir.config(bg=colors['bg_main'], fg=colors['fg_main'])
        entry_border = colors.get('entry_border', colors['border'])
        self.entry_dir.config(
            bg=colors['entry_bg'], 
            fg=colors['entry_fg'],
            highlightcolor=entry_border,
            highlightbackground=entry_border,
            highlightthickness=1,
            insertbackground=colors['fg_main'],
            relief="solid",
            bd=1
        )
        self.btn_browse.config(
            bg=colors['primary'],
            fg='white',
            activebackground=colors['primary_hover'],
            activeforeground='white'
        )


# ================== 标签页1: 序号重命名 ==================
class NumRenameTab(tk.Frame):
    """序号重命名标签页 - 支持前缀/后缀切换"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.only_num_var = tk.BooleanVar(value=False)
        self.reverse_var = tk.BooleanVar(value=False)
        self.old_start_var = tk.StringVar()
        self.old_end_var = tk.StringVar()
        self.new_start_var = tk.StringVar()
        self.new_end_var = tk.StringVar()
        self.num_group_var = tk.StringVar(value="1")
        self.pad_width_var = tk.StringVar(value="")
        self.is_prefix_var = tk.BooleanVar(value=True)  # True=前缀, False=后缀
        
        self._placeholder_text = ""
        self._ext_placeholder_text = ""
        self._is_placeholder_shown = False
        self._is_ext_placeholder_shown = False
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        
        # ===== 分组1: 编号范围设置 =====
        range_frame = tk.LabelFrame(self, text="编号范围设置", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        range_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(0, ROW_PADDING * 2))
        range_frame.columnconfigure(0, weight=1)
        self.range_frame = range_frame
        
        # 第1行：当前范围 → 目标范围
        row1 = tk.Frame(range_frame)
        row1.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        self.lbl_old_range = tk.Label(row1, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_old_range.pack(side='left')
        
        self.old_start = tk.Entry(
            row1, textvariable=self.old_start_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_SMALL, 
            relief="solid", bd=1, justify="center"
        )
        self.old_start.pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_tilde1 = tk.Label(row1, text="~", font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_tilde1.pack(side='left')
        
        self.old_end = tk.Entry(
            row1, textvariable=self.old_end_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_SMALL, 
            relief="solid", bd=1, justify="center"
        )
        self.old_end.pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_arrow = tk.Label(row1, text="  ➔  ", font=(FONT_FAMILY, FONT_SIZE_LARGE))
        self.lbl_arrow.pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_new_range = tk.Label(row1, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_new_range.pack(side='left')
        
        self.new_start = tk.Entry(
            row1, textvariable=self.new_start_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_SMALL, 
            relief="solid", bd=1, justify="center"
        )
        self.new_start.pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_tilde2 = tk.Label(row1, text="~", font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_tilde2.pack(side='left')
        
        self.new_end = tk.Entry(
            row1, textvariable=self.new_end_var,
            font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"), width=10,
            state='readonly', relief="solid", bd=1, justify="center"
        )
        self.new_end.pack(side='left', padx=SPACING_SMALL)
        
        # 第2行：数字组
        row2 = tk.Frame(range_frame)
        row2.grid(row=1, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)

        self.lbl_num_group = tk.Label(row2, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_num_group.grid(row=0, column=0, sticky='w')

        self.num_group_spin = tk.Spinbox(
            row2, from_=1, to=10, width=4,
            textvariable=self.num_group_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), relief="solid", bd=1, justify="center"
        )
        self.num_group_spin.grid(row=0, column=1, padx=SPACING_SMALL, sticky='w')

        self.lbl_num_group_tip = tk.Label(
            row2, font=(FONT_FAMILY, FONT_SIZE_SMALL), fg="gray"
        )
        self.lbl_num_group_tip.grid(row=0, column=2, padx=SPACING_SMALL, sticky='w')
        
        # 第3行：补零 + 倒序 + 扩展名
        row3 = tk.Frame(range_frame)
        row3.grid(row=2, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)

        self.lbl_pad_width = tk.Label(row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_pad_width.grid(row=0, column=0, sticky='w')

        self.pad_width_spin = tk.Spinbox(
            row3, from_=1, to=10, width=4,
            textvariable=self.pad_width_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), relief="solid", bd=1, justify="center"
        )
        self.pad_width_spin.grid(row=0, column=1, padx=SPACING_SMALL, sticky='w')

        self.lbl_pad_tip = tk.Label(
            row3, font=(FONT_FAMILY, FONT_SIZE_SMALL), fg="gray"
        )
        self.lbl_pad_tip.grid(row=0, column=2, padx=SPACING_SMALL, sticky='w')

        tk.Label(row3, text="|", font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="gray").grid(row=0, column=3, padx=SPACING_LARGE, sticky='w')

        self.chk_reverse = tk.Checkbutton(
            row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            variable=self.reverse_var
        )
        self.chk_reverse.grid(row=0, column=4, sticky='w')
        
        # 第4行：扩展名筛选
        row4 = tk.Frame(range_frame)
        row4.grid(row=3, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        self.lbl_ext_filter = tk.Label(row4, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_ext_filter.pack(side='left')
        
        self.ext_entry = tk.Entry(
            row4, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_LARGE, 
            relief="solid", bd=1
        )
        self.ext_entry.pack(side='left', padx=SPACING_SMALL)
        
        # ===== 分组2: 文件名格式 =====
        name_frame = tk.LabelFrame(self, text="文件名格式", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        name_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=ROW_PADDING)
        name_frame.columnconfigure(0, weight=1)
        self.name_frame = name_frame
        
        row5 = tk.Frame(name_frame)
        row5.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        # 位置选择（前缀/后缀）
        self.lbl_position = tk.Label(row5, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_position.pack(side='left')
        
        self.pos_combo = ttk.Combobox(
            row5, values=["前缀", "后缀"], 
            state="readonly", width=6, 
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        self.pos_combo.pack(side='left', padx=SPACING_SMALL)
        self.pos_combo.set("前缀")
        self.pos_combo.bind("<<ComboboxSelected>>", self._on_position_change)
        
        # 分隔线
        tk.Label(row5, text="|", font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="gray").pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_prefix = tk.Label(row5, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_prefix.pack(side='left')
        
        self.prefix_entry = tk.Entry(
            row5, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_MEDIUM, 
            relief="solid", bd=1
        )
        self.prefix_entry.pack(side='left', padx=SPACING_SMALL)
        
        self.chk_only_num = tk.Checkbutton(
            row5, font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            variable=self.only_num_var, command=self._toggle_prefix
        )
        self.chk_only_num.pack(side='left', padx=SPACING_LARGE)
    
    def _setup_bindings(self):
        self.old_start_var.trace_add("write", self._update_end)
        self.old_end_var.trace_add("write", self._update_end)
        self.new_start_var.trace_add("write", self._update_end)
        
        self.prefix_entry.bind("<FocusIn>", self._on_prefix_focus_in)
        self.prefix_entry.bind("<FocusOut>", self._on_prefix_focus_out)
        
        self.ext_entry.bind("<FocusIn>", self._on_ext_focus_in)
        self.ext_entry.bind("<FocusOut>", self._on_ext_focus_out)
    
    def _on_position_change(self, event=None):
        """位置切换时更新内部状态"""
        # 用下拉框选中项的位置索引判断是前缀还是后缀（候选列表顺序固定为 [前缀项, 后缀项]），
        # 不再比较具体文字，这样任何语言都能正确识别
        self.is_prefix_var.set(self.pos_combo.current() == 0)
    
    def _on_ext_focus_in(self, event):
        if self._is_ext_placeholder_shown:
            self.ext_entry.delete(0, tk.END)
            self.ext_entry.config(fg=getattr(self, '_entry_fg', 'black'))
            self._is_ext_placeholder_shown = False
    
    def _on_ext_focus_out(self, event):
        if not self.ext_entry.get().strip():
            self._show_ext_placeholder()
    
    def _show_ext_placeholder(self):
        if self._ext_placeholder_text:
            self.ext_entry.delete(0, tk.END)
            self.ext_entry.insert(0, self._ext_placeholder_text)
            self.ext_entry.config(fg='gray')
            self._is_ext_placeholder_shown = True
    
    def _on_prefix_focus_in(self, event):
        if self._is_placeholder_shown and not self.only_num_var.get():
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.config(fg=getattr(self, '_entry_fg', 'black'))
            self._is_placeholder_shown = False
    
    def _on_prefix_focus_out(self, event):
        if not self.prefix_entry.get().strip() and not self.only_num_var.get():
            self._show_placeholder()
    
    def _show_placeholder(self):
        if self._placeholder_text and not self.only_num_var.get():
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.insert(0, self._placeholder_text)
            self.prefix_entry.config(fg='gray')
            self._is_placeholder_shown = True
    
    def _update_end(self, *args):
        try:
            old_s_str = self.old_start_var.get().strip()
            old_e_str = self.old_end_var.get().strip()
            new_s_str = self.new_start_var.get().strip()
            
            if not old_s_str or not old_e_str or not new_s_str:
                self.new_end_var.set("?")
                return
                
            old_s = int(old_s_str)
            old_e = int(old_e_str)
            new_s = int(new_s_str)
            
            if old_e < old_s:
                self.new_end_var.set("无效范围")
                return
            self.new_end_var.set(str(new_s + (old_e - old_s)))
        except ValueError:
            self.new_end_var.set("?")
    
    def _toggle_prefix(self):
        """切换前缀/后缀模式"""
        if self.only_num_var.get():
            self.prefix_entry.config(state='disabled')
            self.pos_combo.config(state='disabled')
            if self._is_placeholder_shown:
                self.prefix_entry.delete(0, tk.END)
                self._is_placeholder_shown = False
        else:
            self.prefix_entry.config(state='normal')
            # 检查 notebook 是否处于 disabled 状态
            try:
                notebook = self.master
                if hasattr(notebook, 'state') and 'disabled' in notebook.state():
                    self.pos_combo.config(state='disabled')
                else:
                    self.pos_combo.config(state='readonly')
            except:
                self.pos_combo.config(state='readonly')
            if not self.prefix_entry.get().strip():
                self._show_placeholder()
    
    def get_values(self):
        val = self.prefix_entry.get().strip()
        if self._is_placeholder_shown or val == self._placeholder_text:
            val = ""
        
        ext_val = self.ext_entry.get().strip()
        if self._is_ext_placeholder_shown or ext_val == self._ext_placeholder_text:
            ext_val = ""
        extensions = [e.strip().lower() for e in ext_val.split(',') if e.strip()]
        extensions = [e if e.startswith('.') else f'.{e}' for e in extensions]
        
        try:
            num_group = int(self.num_group_var.get().strip() or 1)
            if num_group < 1:
                num_group = 1
        except ValueError:
            num_group = 1
        
        try:
            pad_width = int(self.pad_width_var.get().strip() or 0)
            if pad_width < 0:
                pad_width = 0
        except ValueError:
            pad_width = 0
        
        # 获取位置
        # 同样用位置索引判断，避免只认识中/英文字面值
        is_prefix = self.pos_combo.current() == 0
        
        return {
            'old_start': self.old_start_var.get(),
            'old_end': self.old_end_var.get(),
            'new_start': self.new_start_var.get(),
            'prefix': val,
            'only_num': self.only_num_var.get(),
            'num_group': num_group,
            'reverse': self.reverse_var.get(),
            'extensions': extensions,
            'pad_width': pad_width,
            'is_prefix': is_prefix,
        }
    
    def set_prefix_placeholder(self, text: str, theme: str):
        self._placeholder_text = text
        if not self.prefix_entry.get().strip() or self._is_placeholder_shown:
            self._show_placeholder()
    
    def set_ext_placeholder(self, text: str):
        self._ext_placeholder_text = text
        if not self.ext_entry.get().strip() or self._is_ext_placeholder_shown:
            self._show_ext_placeholder()
    
    def set_language(self, lang_dict: dict):
        self.range_frame.config(text=lang_dict.get('lbl_range_setting', "编号范围设置"))
        self.name_frame.config(text=lang_dict.get('lbl_name_format', "文件名格式"))
        
        self.lbl_old_range.config(text=lang_dict['lbl_old_range'])
        self.lbl_new_range.config(text=lang_dict['lbl_new_range'])
        self.lbl_prefix.config(text=lang_dict['lbl_prefix'])
        self.chk_only_num.config(text=lang_dict['chk_only_num'])
        self.lbl_num_group.config(text=lang_dict['lbl_num_group'])
        self.lbl_num_group_tip.config(text=lang_dict['num_group_tip'])
        self.chk_reverse.config(text=lang_dict['chk_reverse'])
        self.lbl_ext_filter.config(text=lang_dict['lbl_ext_filter'])
        self.lbl_pad_width.config(text=lang_dict['lbl_pad_width'])
        self.lbl_pad_tip.config(text=lang_dict['pad_tip'])
        self.lbl_position.config(text=lang_dict.get('lbl_position', "位置:"))
        self.pos_combo.config(values=[lang_dict.get('pos_prefix', "前缀"), lang_dict.get('pos_suffix', "后缀")])
        self.pos_combo.current(0 if self.is_prefix_var.get() else 1)
        self.set_ext_placeholder(lang_dict['ext_placeholder'])
    
    def apply_theme(self, colors: dict):
        self._entry_fg = colors.get('entry_fg', 'black')
        self.configure(bg=colors['bg_main'])
        
        for frame in [self.range_frame, self.name_frame]:
            frame.configure(bg=colors['bg_main'], fg=colors['fg_main'])
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=colors['bg_main'])
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Label):
                            subchild.config(bg=colors['bg_main'], fg=colors['fg_main'])
                        elif isinstance(subchild, tk.Checkbutton):
                            subchild.config(
                                bg=colors['bg_main'],
                                fg=colors['fg_main'],
                                selectcolor=colors['bg_card'],
                                activebackground=colors['bg_main'],
                                activeforeground=colors['fg_main']
                            )
        
        for lbl in [self.lbl_old_range, self.lbl_new_range, self.lbl_prefix, self.lbl_position,
                    self.lbl_tilde1, self.lbl_tilde2, self.lbl_arrow,
                    self.lbl_num_group, self.lbl_num_group_tip,
                    self.lbl_ext_filter, self.lbl_pad_width, self.lbl_pad_tip]:
            lbl.config(bg=colors['bg_main'], fg=colors['fg_main'])
        
        entry_border = colors.get('entry_border', colors['border'])
        for entry in [self.old_start, self.old_end, self.new_start, 
                      self.prefix_entry, self.num_group_spin,
                      self.ext_entry, self.pad_width_spin]:
            entry.config(
                bg=colors['entry_bg'],
                fg=colors['entry_fg'],
                highlightcolor=entry_border,
                highlightbackground=entry_border,
                highlightthickness=1,
                insertbackground=colors['fg_main'],
                relief="solid",
                bd=1
            )
            if entry in [self.num_group_spin, self.pad_width_spin]:
                try:
                    entry.config(buttonbackground=colors['tree_heading'])
                except:
                    pass
        
        self.new_end.config(
            bg=colors['tree_heading'],
            fg=colors['fg_sub'],
            highlightcolor=entry_border,
            highlightbackground=entry_border,
            highlightthickness=1,
            relief="solid",
            bd=1
        )
        
        for chk in [self.chk_only_num, self.chk_reverse]:
            chk.config(
                bg=colors['bg_main'],
                fg=colors['fg_main'],
                selectcolor=colors['bg_card'],
                activebackground=colors['bg_main'],
                activeforeground=colors['fg_main']
            )


# ================== 标签页2: 按顺序重命名 ==================
class OrderRenameTab(tk.Frame):
    """按文件名顺序重命名标签页"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.only_num_var = tk.BooleanVar(value=False)
        self.reverse_var = tk.BooleanVar(value=False)
        self.new_start_var = tk.StringVar(value="1")
        self.pad_width_var = tk.StringVar(value="")
        self.is_prefix_var = tk.BooleanVar(value=True)
        
        self._placeholder_text = ""
        self._ext_placeholder_text = ""
        self._is_placeholder_shown = False
        self._is_ext_placeholder_shown = False
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        
        # ===== 分组1: 排序设置 =====
        order_frame = tk.LabelFrame(self, text="排序设置", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        order_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(0, ROW_PADDING * 2))
        order_frame.columnconfigure(0, weight=1)
        self.order_frame = order_frame
        
        row1 = tk.Frame(order_frame)
        row1.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        self.chk_reverse = tk.Checkbutton(
            row1, font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            variable=self.reverse_var
        )
        self.chk_reverse.pack(side='left')
        
        self.lbl_order_tip = tk.Label(
            row1, font=(FONT_FAMILY, FONT_SIZE_SMALL), fg="gray"
        )
        self.lbl_order_tip.pack(side='left', padx=SPACING_LARGE)
        
        # ===== 分组2: 编号设置 =====
        num_frame = tk.LabelFrame(self, text="编号设置", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        num_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=(0, ROW_PADDING * 2))
        num_frame.columnconfigure(0, weight=1)
        self.num_frame = num_frame
        
        row2 = tk.Frame(num_frame)
        row2.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        self.lbl_new_range = tk.Label(row2, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_new_range.pack(side='left')
        
        self.new_start = tk.Entry(
            row2, textvariable=self.new_start_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_SMALL, 
            relief="solid", bd=1, justify="center"
        )
        self.new_start.pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_start_tip = tk.Label(
            row2, font=(FONT_FAMILY, FONT_SIZE_SMALL), fg="gray"
        )
        self.lbl_start_tip.pack(side='left', padx=SPACING_SMALL)
        
        tk.Label(row2, text="|", font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="gray").pack(side='left', padx=SPACING_LARGE)
        
        self.lbl_pad_width = tk.Label(row2, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_pad_width.pack(side='left')
        
        self.pad_width_spin = tk.Spinbox(
            row2, from_=1, to=10, width=4,
            textvariable=self.pad_width_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), relief="solid", bd=1, justify="center"
        )
        self.pad_width_spin.pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_pad_tip = tk.Label(
            row2, font=(FONT_FAMILY, FONT_SIZE_SMALL), fg="gray"
        )
        self.lbl_pad_tip.pack(side='left', padx=SPACING_SMALL)
        
        # ===== 分组3: 文件名格式 =====
        name_frame = tk.LabelFrame(self, text="文件名格式", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        name_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=(0, ROW_PADDING * 2))
        name_frame.columnconfigure(0, weight=1)
        self.name_frame = name_frame
        
        row3 = tk.Frame(name_frame)
        row3.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        # 位置选择（前缀/后缀）
        self.lbl_position = tk.Label(row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_position.pack(side='left')
        
        self.pos_combo = ttk.Combobox(
            row3, values=["前缀", "后缀"], 
            state="readonly", width=6, 
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        self.pos_combo.pack(side='left', padx=SPACING_SMALL)
        self.pos_combo.set("前缀")
        self.pos_combo.bind("<<ComboboxSelected>>", self._on_position_change)
        
        tk.Label(row3, text="|", font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="gray").pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_prefix = tk.Label(row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_prefix.pack(side='left')
        
        self.prefix_entry = tk.Entry(
            row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_MEDIUM, 
            relief="solid", bd=1
        )
        self.prefix_entry.pack(side='left', padx=SPACING_SMALL)
        
        self.chk_only_num = tk.Checkbutton(
            row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            variable=self.only_num_var, command=self._toggle_prefix
        )
        self.chk_only_num.pack(side='left', padx=SPACING_LARGE)
        
        # ===== 分组4: 文件筛选 =====
        ext_frame = tk.LabelFrame(self, text="文件筛选", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        ext_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=ROW_PADDING)
        ext_frame.columnconfigure(0, weight=1)
        self.ext_frame = ext_frame
        
        row4 = tk.Frame(ext_frame)
        row4.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        self.lbl_ext_filter = tk.Label(row4, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_ext_filter.pack(side='left')
        
        self.ext_entry = tk.Entry(
            row4, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_LARGE, 
            relief="solid", bd=1
        )
        self.ext_entry.pack(side='left', padx=SPACING_SMALL)
    
    def _setup_bindings(self):
        self.prefix_entry.bind("<FocusIn>", self._on_prefix_focus_in)
        self.prefix_entry.bind("<FocusOut>", self._on_prefix_focus_out)
        self.ext_entry.bind("<FocusIn>", self._on_ext_focus_in)
        self.ext_entry.bind("<FocusOut>", self._on_ext_focus_out)
    
    def _on_position_change(self, event=None):
        # 用下拉框选中项的位置索引判断是前缀还是后缀（候选列表顺序固定为 [前缀项, 后缀项]），
        # 不再比较具体文字，这样任何语言都能正确识别
        self.is_prefix_var.set(self.pos_combo.current() == 0)
    
    def _on_ext_focus_in(self, event):
        if self._is_ext_placeholder_shown:
            self.ext_entry.delete(0, tk.END)
            self.ext_entry.config(fg=getattr(self, '_entry_fg', 'black'))
            self._is_ext_placeholder_shown = False
    
    def _on_ext_focus_out(self, event):
        if not self.ext_entry.get().strip():
            self._show_ext_placeholder()
    
    def _show_ext_placeholder(self):
        if self._ext_placeholder_text:
            self.ext_entry.delete(0, tk.END)
            self.ext_entry.insert(0, self._ext_placeholder_text)
            self.ext_entry.config(fg='gray')
            self._is_ext_placeholder_shown = True
    
    def _on_prefix_focus_in(self, event):
        if self._is_placeholder_shown and not self.only_num_var.get():
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.config(fg=getattr(self, '_entry_fg', 'black'))
            self._is_placeholder_shown = False
    
    def _on_prefix_focus_out(self, event):
        if not self.prefix_entry.get().strip() and not self.only_num_var.get():
            self._show_placeholder()
    
    def _show_placeholder(self):
        if self._placeholder_text and not self.only_num_var.get():
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.insert(0, self._placeholder_text)
            self.prefix_entry.config(fg='gray')
            self._is_placeholder_shown = True
    
    def _toggle_prefix(self):
        """切换前缀/后缀模式"""
        if self.only_num_var.get():
            self.prefix_entry.config(state='disabled')
            self.pos_combo.config(state='disabled')
            if self._is_placeholder_shown:
                self.prefix_entry.delete(0, tk.END)
                self._is_placeholder_shown = False
        else:
            self.prefix_entry.config(state='normal')
            # 检查 notebook 是否处于 disabled 状态
            try:
                notebook = self.master
                if hasattr(notebook, 'state') and 'disabled' in notebook.state():
                    self.pos_combo.config(state='disabled')
                else:
                    self.pos_combo.config(state='readonly')
            except:
                self.pos_combo.config(state='readonly')
            if not self.prefix_entry.get().strip():
                self._show_placeholder()
    
    def get_values(self):
        val = self.prefix_entry.get().strip()
        if self._is_placeholder_shown or val == self._placeholder_text:
            val = ""
        
        ext_val = self.ext_entry.get().strip()
        if self._is_ext_placeholder_shown or ext_val == self._ext_placeholder_text:
            ext_val = ""
        extensions = [e.strip().lower() for e in ext_val.split(',') if e.strip()]
        extensions = [e if e.startswith('.') else f'.{e}' for e in extensions]
        
        try:
            pad_width = int(self.pad_width_var.get().strip() or 0)
            if pad_width < 0:
                pad_width = 0
        except ValueError:
            pad_width = 0
        
        try:
            new_start = int(self.new_start_var.get().strip() or 1)
        except ValueError:
            new_start = 1
        
        # 同样用位置索引判断，避免只认识中/英文字面值
        is_prefix = self.pos_combo.current() == 0
        
        return {
            'prefix': val,
            'only_num': self.only_num_var.get(),
            'reverse': self.reverse_var.get(),
            'extensions': extensions,
            'pad_width': pad_width,
            'new_start': new_start,
            'is_prefix': is_prefix,
        }
    
    def set_prefix_placeholder(self, text: str, theme: str):
        self._placeholder_text = text
        if not self.prefix_entry.get().strip() or self._is_placeholder_shown:
            self._show_placeholder()
    
    def set_ext_placeholder(self, text: str):
        self._ext_placeholder_text = text
        if not self.ext_entry.get().strip() or self._is_ext_placeholder_shown:
            self._show_ext_placeholder()
    
    def set_language(self, lang_dict: dict):
        self.order_frame.config(text=lang_dict.get('lbl_sort_setting', "排序设置"))
        self.num_frame.config(text=lang_dict.get('lbl_num_setting', "编号设置"))
        self.name_frame.config(text=lang_dict.get('lbl_name_format', "文件名格式"))
        self.ext_frame.config(text=lang_dict.get('lbl_file_filter', "文件筛选"))
        
        self.chk_reverse.config(text=lang_dict['chk_reverse'])
        self.lbl_order_tip.config(text=lang_dict.get('order_tip', "按文件名顺序（A→Z）"))
        self.lbl_new_range.config(text=lang_dict.get('lbl_start_num', "起始编号:"))
        self.lbl_start_tip.config(text="")
        self.lbl_pad_width.config(text=lang_dict['lbl_pad_width'])
        self.lbl_pad_tip.config(text=lang_dict['pad_tip'])
        self.lbl_prefix.config(text=lang_dict['lbl_prefix'])
        self.chk_only_num.config(text=lang_dict['chk_only_num'])
        self.lbl_ext_filter.config(text=lang_dict['lbl_ext_filter'])
        self.lbl_position.config(text=lang_dict.get('lbl_position', "位置:"))
        self.pos_combo.config(values=[lang_dict.get('pos_prefix', "前缀"), lang_dict.get('pos_suffix', "后缀")])
        self.pos_combo.current(0 if self.is_prefix_var.get() else 1)
        self.set_ext_placeholder(lang_dict['ext_placeholder'])
    
    def apply_theme(self, colors: dict):
        self._entry_fg = colors.get('entry_fg', 'black')
        self.configure(bg=colors['bg_main'])
        
        for frame in [self.order_frame, self.num_frame, self.name_frame, self.ext_frame]:
            frame.configure(bg=colors['bg_main'], fg=colors['fg_main'])
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=colors['bg_main'])
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Label):
                            subchild.config(bg=colors['bg_main'], fg=colors['fg_main'])
                        elif isinstance(subchild, tk.Checkbutton):
                            subchild.config(
                                bg=colors['bg_main'],
                                fg=colors['fg_main'],
                                selectcolor=colors['bg_card'],
                                activebackground=colors['bg_main'],
                                activeforeground=colors['fg_main']
                            )
        
        for lbl in [self.lbl_prefix, self.lbl_position, self.lbl_pad_width, self.lbl_pad_tip,
                    self.lbl_ext_filter, self.lbl_order_tip,
                    self.lbl_new_range, self.lbl_start_tip]:
            lbl.config(bg=colors['bg_main'], fg=colors['fg_main'])
        
        entry_border = colors.get('entry_border', colors['border'])
        for entry in [self.prefix_entry, self.pad_width_spin, self.ext_entry, self.new_start]:
            entry.config(
                bg=colors['entry_bg'],
                fg=colors['entry_fg'],
                highlightcolor=entry_border,
                highlightbackground=entry_border,
                highlightthickness=1,
                insertbackground=colors['fg_main'],
                relief="solid",
                bd=1
            )
            if entry == self.pad_width_spin:
                try:
                    entry.config(buttonbackground=colors['tree_heading'])
                except:
                    pass
        
        for chk in [self.chk_only_num, self.chk_reverse]:
            chk.config(
                bg=colors['bg_main'],
                fg=colors['fg_main'],
                selectcolor=colors['bg_card'],
                activebackground=colors['bg_main'],
                activeforeground=colors['fg_main']
            )


# ================== 标签页3: 按时间重命名 ==================
class TimeRenameTab(tk.Frame):
    """按修改时间重命名标签页"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.only_num_var = tk.BooleanVar(value=False)
        self.reverse_var = tk.BooleanVar(value=False)
        self.new_start_var = tk.StringVar(value="1")
        self.pad_width_var = tk.StringVar(value="")
        self.is_prefix_var = tk.BooleanVar(value=True)
        
        self._placeholder_text = ""
        self._ext_placeholder_text = ""
        self._is_placeholder_shown = False
        self._is_ext_placeholder_shown = False
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        
        # ===== 分组1: 排序设置 =====
        order_frame = tk.LabelFrame(self, text="排序设置", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        order_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(0, ROW_PADDING * 2))
        order_frame.columnconfigure(0, weight=1)
        self.order_frame = order_frame
        
        row1 = tk.Frame(order_frame)
        row1.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        self.chk_reverse = tk.Checkbutton(
            row1, font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            variable=self.reverse_var
        )
        self.chk_reverse.pack(side='left')
        
        self.lbl_order_tip = tk.Label(
            row1, font=(FONT_FAMILY, FONT_SIZE_SMALL), fg="gray"
        )
        self.lbl_order_tip.pack(side='left', padx=SPACING_LARGE)
        
        # ===== 分组2: 编号设置 =====
        num_frame = tk.LabelFrame(self, text="编号设置", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        num_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=(0, ROW_PADDING * 2))
        num_frame.columnconfigure(0, weight=1)
        self.num_frame = num_frame
        
        row2 = tk.Frame(num_frame)
        row2.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        self.lbl_new_range = tk.Label(row2, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_new_range.pack(side='left')
        
        self.new_start = tk.Entry(
            row2, textvariable=self.new_start_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_SMALL, 
            relief="solid", bd=1, justify="center"
        )
        self.new_start.pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_start_tip = tk.Label(
            row2, font=(FONT_FAMILY, FONT_SIZE_SMALL), fg="gray"
        )
        self.lbl_start_tip.pack(side='left', padx=SPACING_SMALL)
        
        tk.Label(row2, text="|", font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="gray").pack(side='left', padx=SPACING_LARGE)
        
        self.lbl_pad_width = tk.Label(row2, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_pad_width.pack(side='left')
        
        self.pad_width_spin = tk.Spinbox(
            row2, from_=1, to=10, width=4,
            textvariable=self.pad_width_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), relief="solid", bd=1, justify="center"
        )
        self.pad_width_spin.pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_pad_tip = tk.Label(
            row2, font=(FONT_FAMILY, FONT_SIZE_SMALL), fg="gray"
        )
        self.lbl_pad_tip.pack(side='left', padx=SPACING_SMALL)
        
        # ===== 分组3: 文件名格式 =====
        name_frame = tk.LabelFrame(self, text="文件名格式", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        name_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=(0, ROW_PADDING * 2))
        name_frame.columnconfigure(0, weight=1)
        self.name_frame = name_frame
        
        row3 = tk.Frame(name_frame)
        row3.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        # 位置选择（前缀/后缀）
        self.lbl_position = tk.Label(row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_position.pack(side='left')
        
        self.pos_combo = ttk.Combobox(
            row3, values=["前缀", "后缀"], 
            state="readonly", width=6, 
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        self.pos_combo.pack(side='left', padx=SPACING_SMALL)
        self.pos_combo.set("前缀")
        self.pos_combo.bind("<<ComboboxSelected>>", self._on_position_change)
        
        tk.Label(row3, text="|", font=(FONT_FAMILY, FONT_SIZE_NORMAL), fg="gray").pack(side='left', padx=SPACING_SMALL)
        
        self.lbl_prefix = tk.Label(row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_prefix.pack(side='left')
        
        self.prefix_entry = tk.Entry(
            row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_MEDIUM, 
            relief="solid", bd=1
        )
        self.prefix_entry.pack(side='left', padx=SPACING_SMALL)
        
        self.chk_only_num = tk.Checkbutton(
            row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            variable=self.only_num_var, command=self._toggle_prefix
        )
        self.chk_only_num.pack(side='left', padx=SPACING_LARGE)
        
        # ===== 分组4: 文件筛选 =====
        ext_frame = tk.LabelFrame(self, text="文件筛选", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        ext_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=ROW_PADDING)
        ext_frame.columnconfigure(0, weight=1)
        self.ext_frame = ext_frame
        
        row4 = tk.Frame(ext_frame)
        row4.grid(row=0, column=0, sticky='w', pady=ROW_PADDING, padx=SPACING_LARGE)
        
        self.lbl_ext_filter = tk.Label(row4, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_ext_filter.pack(side='left')
        
        self.ext_entry = tk.Entry(
            row4, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_LARGE, 
            relief="solid", bd=1
        )
        self.ext_entry.pack(side='left', padx=SPACING_SMALL)
    
    def _setup_bindings(self):
        self.prefix_entry.bind("<FocusIn>", self._on_prefix_focus_in)
        self.prefix_entry.bind("<FocusOut>", self._on_prefix_focus_out)
        self.ext_entry.bind("<FocusIn>", self._on_ext_focus_in)
        self.ext_entry.bind("<FocusOut>", self._on_ext_focus_out)
    
    def _on_position_change(self, event=None):
        # 用下拉框选中项的位置索引判断是前缀还是后缀（候选列表顺序固定为 [前缀项, 后缀项]），
        # 不再比较具体文字，这样任何语言都能正确识别
        self.is_prefix_var.set(self.pos_combo.current() == 0)
    
    def _on_ext_focus_in(self, event):
        if self._is_ext_placeholder_shown:
            self.ext_entry.delete(0, tk.END)
            self.ext_entry.config(fg=getattr(self, '_entry_fg', 'black'))
            self._is_ext_placeholder_shown = False
    
    def _on_ext_focus_out(self, event):
        if not self.ext_entry.get().strip():
            self._show_ext_placeholder()
    
    def _show_ext_placeholder(self):
        if self._ext_placeholder_text:
            self.ext_entry.delete(0, tk.END)
            self.ext_entry.insert(0, self._ext_placeholder_text)
            self.ext_entry.config(fg='gray')
            self._is_ext_placeholder_shown = True
    
    def _on_prefix_focus_in(self, event):
        if self._is_placeholder_shown and not self.only_num_var.get():
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.config(fg=getattr(self, '_entry_fg', 'black'))
            self._is_placeholder_shown = False
    
    def _on_prefix_focus_out(self, event):
        if not self.prefix_entry.get().strip() and not self.only_num_var.get():
            self._show_placeholder()
    
    def _show_placeholder(self):
        if self._placeholder_text and not self.only_num_var.get():
            self.prefix_entry.delete(0, tk.END)
            self.prefix_entry.insert(0, self._placeholder_text)
            self.prefix_entry.config(fg='gray')
            self._is_placeholder_shown = True
    
    def _toggle_prefix(self):
        """切换前缀/后缀模式"""
        if self.only_num_var.get():
            self.prefix_entry.config(state='disabled')
            self.pos_combo.config(state='disabled')
            if self._is_placeholder_shown:
                self.prefix_entry.delete(0, tk.END)
                self._is_placeholder_shown = False
        else:
            self.prefix_entry.config(state='normal')
            # 检查 notebook 是否处于 disabled 状态
            try:
                notebook = self.master
                if hasattr(notebook, 'state') and 'disabled' in notebook.state():
                    self.pos_combo.config(state='disabled')
                else:
                    self.pos_combo.config(state='readonly')
            except:
                self.pos_combo.config(state='readonly')
            if not self.prefix_entry.get().strip():
                self._show_placeholder()
    
    def get_values(self):
        val = self.prefix_entry.get().strip()
        if self._is_placeholder_shown or val == self._placeholder_text:
            val = ""
        
        ext_val = self.ext_entry.get().strip()
        if self._is_ext_placeholder_shown or ext_val == self._ext_placeholder_text:
            ext_val = ""
        extensions = [e.strip().lower() for e in ext_val.split(',') if e.strip()]
        extensions = [e if e.startswith('.') else f'.{e}' for e in extensions]
        
        try:
            pad_width = int(self.pad_width_var.get().strip() or 0)
            if pad_width < 0:
                pad_width = 0
        except ValueError:
            pad_width = 0
        
        try:
            new_start = int(self.new_start_var.get().strip() or 1)
        except ValueError:
            new_start = 1
        
        # 同样用位置索引判断，避免只认识中/英文字面值
        is_prefix = self.pos_combo.current() == 0
        
        return {
            'prefix': val,
            'only_num': self.only_num_var.get(),
            'reverse': self.reverse_var.get(),
            'extensions': extensions,
            'pad_width': pad_width,
            'new_start': new_start,
            'is_prefix': is_prefix,
        }
    
    def set_prefix_placeholder(self, text: str, theme: str):
        self._placeholder_text = text
        if not self.prefix_entry.get().strip() or self._is_placeholder_shown:
            self._show_placeholder()
    
    def set_ext_placeholder(self, text: str):
        self._ext_placeholder_text = text
        if not self.ext_entry.get().strip() or self._is_ext_placeholder_shown:
            self._show_ext_placeholder()
    
    def set_language(self, lang_dict: dict):
        self.order_frame.config(text=lang_dict.get('lbl_sort_setting', "排序设置"))
        self.num_frame.config(text=lang_dict.get('lbl_num_setting', "编号设置"))
        self.name_frame.config(text=lang_dict.get('lbl_name_format', "文件名格式"))
        self.ext_frame.config(text=lang_dict.get('lbl_file_filter', "文件筛选"))
        
        self.chk_reverse.config(text=lang_dict['chk_reverse'])
        self.lbl_order_tip.config(text=lang_dict.get('time_tip', "按修改时间（旧→新）"))
        self.lbl_new_range.config(text=lang_dict.get('lbl_start_num', "起始编号:"))
        self.lbl_start_tip.config(text="")
        self.lbl_pad_width.config(text=lang_dict['lbl_pad_width'])
        self.lbl_pad_tip.config(text=lang_dict['pad_tip'])
        self.lbl_prefix.config(text=lang_dict['lbl_prefix'])
        self.chk_only_num.config(text=lang_dict['chk_only_num'])
        self.lbl_ext_filter.config(text=lang_dict['lbl_ext_filter'])
        self.lbl_position.config(text=lang_dict.get('lbl_position', "位置:"))
        self.pos_combo.config(values=[lang_dict.get('pos_prefix', "前缀"), lang_dict.get('pos_suffix', "后缀")])
        self.pos_combo.current(0 if self.is_prefix_var.get() else 1)
        self.set_ext_placeholder(lang_dict['ext_placeholder'])
    
    def apply_theme(self, colors: dict):
        self._entry_fg = colors.get('entry_fg', 'black')
        self.configure(bg=colors['bg_main'])
        
        for frame in [self.order_frame, self.num_frame, self.name_frame, self.ext_frame]:
            frame.configure(bg=colors['bg_main'], fg=colors['fg_main'])
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=colors['bg_main'])
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Label):
                            subchild.config(bg=colors['bg_main'], fg=colors['fg_main'])
                        elif isinstance(subchild, tk.Checkbutton):
                            subchild.config(
                                bg=colors['bg_main'],
                                fg=colors['fg_main'],
                                selectcolor=colors['bg_card'],
                                activebackground=colors['bg_main'],
                                activeforeground=colors['fg_main']
                            )
        
        for lbl in [self.lbl_prefix, self.lbl_position, self.lbl_pad_width, self.lbl_pad_tip,
                    self.lbl_ext_filter, self.lbl_order_tip,
                    self.lbl_new_range, self.lbl_start_tip]:
            lbl.config(bg=colors['bg_main'], fg=colors['fg_main'])
        
        entry_border = colors.get('entry_border', colors['border'])
        for entry in [self.prefix_entry, self.pad_width_spin, self.ext_entry, self.new_start]:
            entry.config(
                bg=colors['entry_bg'],
                fg=colors['entry_fg'],
                highlightcolor=entry_border,
                highlightbackground=entry_border,
                highlightthickness=1,
                insertbackground=colors['fg_main'],
                relief="solid",
                bd=1
            )
            if entry == self.pad_width_spin:
                try:
                    entry.config(buttonbackground=colors['tree_heading'])
                except:
                    pass
        
        for chk in [self.chk_only_num, self.chk_reverse]:
            chk.config(
                bg=colors['bg_main'],
                fg=colors['fg_main'],
                selectcolor=colors['bg_card'],
                activebackground=colors['bg_main'],
                activeforeground=colors['fg_main']
            )


# ================== 标签页4: 查找与替换 ==================
class ReplaceRenameTab(tk.Frame):
    """查找替换标签页"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.regex_var = tk.BooleanVar(value=False)
        
        self._ext_placeholder_text = ""
        self._is_ext_placeholder_shown = False
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        
        # 查找设置
        find_frame = tk.LabelFrame(self, text="查找设置", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        find_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=ROW_PADDING)
        find_frame.columnconfigure(1, weight=1)
        self.find_frame = find_frame
        
        row1 = tk.Frame(find_frame)
        row1.grid(row=0, column=0, sticky='w', pady=ROW_PADDING * 2, padx=SPACING_LARGE)
        
        self.lbl_find = tk.Label(
            row1, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=12, anchor='w'
        )
        self.lbl_find.pack(side='left')
        
        self.entry_find = tk.Entry(
            row1, textvariable=self.find_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), relief="solid", bd=1, width=35
        )
        self.entry_find.pack(side='left', padx=SPACING_SMALL)
        
        self.chk_regex = tk.Checkbutton(
            row1, font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            variable=self.regex_var
        )
        self.chk_regex.pack(side='left', padx=SPACING_LARGE)
        
        # 替换设置
        replace_frame = tk.LabelFrame(self, text="替换设置", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        replace_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=ROW_PADDING)
        replace_frame.columnconfigure(1, weight=1)
        self.replace_frame = replace_frame
        
        row2 = tk.Frame(replace_frame)
        row2.grid(row=0, column=0, sticky='w', pady=ROW_PADDING * 2, padx=SPACING_LARGE)
        
        self.lbl_replace = tk.Label(
            row2, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=12, anchor='w'
        )
        self.lbl_replace.pack(side='left')
        
        self.entry_replace = tk.Entry(
            row2, textvariable=self.replace_var,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL), relief="solid", bd=1, width=35
        )
        self.entry_replace.pack(side='left', padx=SPACING_SMALL)
        
        # ===== 新增：文件筛选 =====
        ext_frame = tk.LabelFrame(self, text="文件筛选", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        ext_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=ROW_PADDING)
        ext_frame.columnconfigure(1, weight=1)
        self.ext_frame = ext_frame
        
        row3 = tk.Frame(ext_frame)
        row3.grid(row=0, column=0, sticky='w', pady=ROW_PADDING * 2, padx=SPACING_LARGE)
        
        self.lbl_ext_filter = tk.Label(row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.lbl_ext_filter.pack(side='left')
        
        self.ext_entry = tk.Entry(
            row3, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=ENTRY_WIDTH_LARGE, 
            relief="solid", bd=1
        )
        self.ext_entry.pack(side='left', padx=SPACING_SMALL)
    
    def _setup_bindings(self):
        self.ext_entry.bind("<FocusIn>", self._on_ext_focus_in)
        self.ext_entry.bind("<FocusOut>", self._on_ext_focus_out)
    
    def _on_ext_focus_in(self, event):
        if self._is_ext_placeholder_shown:
            self.ext_entry.delete(0, tk.END)
            self.ext_entry.config(fg=getattr(self, '_entry_fg', 'black'))
            self._is_ext_placeholder_shown = False
    
    def _on_ext_focus_out(self, event):
        if not self.ext_entry.get().strip():
            self._show_ext_placeholder()
    
    def _show_ext_placeholder(self):
        if self._ext_placeholder_text:
            self.ext_entry.delete(0, tk.END)
            self.ext_entry.insert(0, self._ext_placeholder_text)
            self.ext_entry.config(fg='gray')
            self._is_ext_placeholder_shown = True
    
    def get_values(self):
        ext_val = self.ext_entry.get().strip()
        if self._is_ext_placeholder_shown or ext_val == self._ext_placeholder_text:
            ext_val = ""
        extensions = [e.strip().lower() for e in ext_val.split(',') if e.strip()]
        extensions = [e if e.startswith('.') else f'.{e}' for e in extensions]
        
        return {
            'find': self.find_var.get(),
            'replace': self.replace_var.get(),
            'use_regex': self.regex_var.get(),
            'extensions': extensions
        }
    
    def set_ext_placeholder(self, text: str):
        self._ext_placeholder_text = text
        if not self.ext_entry.get().strip() or self._is_ext_placeholder_shown:
            self._show_ext_placeholder()
    
    def set_language(self, lang_dict: dict):
        self.find_frame.config(text=lang_dict.get('lbl_find_setting', "查找设置"))
        self.replace_frame.config(text=lang_dict.get('lbl_replace_setting', "替换设置"))
        self.ext_frame.config(text=lang_dict.get('lbl_file_filter', "文件筛选"))
        self.lbl_find.config(text=lang_dict['lbl_find'])
        self.lbl_replace.config(text=lang_dict['lbl_replace'])
        self.chk_regex.config(text=lang_dict['chk_regex'])
        self.lbl_ext_filter.config(text=lang_dict['lbl_ext_filter'])
        self.set_ext_placeholder(lang_dict['ext_placeholder'])
    
    def apply_theme(self, colors: dict):
        self._entry_fg = colors.get('entry_fg', 'black')
        self.configure(bg=colors['bg_main'])
        
        for frame in [self.find_frame, self.replace_frame, self.ext_frame]:
            frame.configure(bg=colors['bg_main'], fg=colors['fg_main'])
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=colors['bg_main'])
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Label):
                            subchild.config(bg=colors['bg_main'], fg=colors['fg_main'])
                        elif isinstance(subchild, tk.Checkbutton):
                            subchild.config(
                                bg=colors['bg_main'],
                                fg=colors['fg_main'],
                                selectcolor=colors['bg_card'],
                                activebackground=colors['bg_main'],
                                activeforeground=colors['fg_main']
                            )
        
        self.lbl_find.config(bg=colors['bg_main'], fg=colors['fg_main'])
        self.lbl_replace.config(bg=colors['bg_main'], fg=colors['fg_main'])
        self.lbl_ext_filter.config(bg=colors['bg_main'], fg=colors['fg_main'])
        
        entry_border = colors.get('entry_border', colors['border'])
        for entry in [self.entry_find, self.entry_replace, self.ext_entry]:
            entry.config(
                bg=colors['entry_bg'],
                fg=colors['entry_fg'],
                highlightcolor=entry_border,
                highlightbackground=entry_border,
                highlightthickness=1,
                insertbackground=colors['fg_main'],
                relief="solid",
                bd=1
            )
        
        self.chk_regex.config(
            bg=colors['bg_main'],
            fg=colors['fg_main'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_main'],
            activeforeground=colors['fg_main']
        )


class ActionButtons(tk.Frame):
    """操作按钮组"""
    def __init__(self, master, on_preview, on_rename, on_undo, **kwargs):
        super().__init__(master, **kwargs)
        self.on_preview = on_preview
        self.on_rename = on_rename
        self.on_undo = on_undo
        
        self._create_widgets()
    
    def _create_widgets(self):
        # 左右各一个空白列，让按钮居中
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=1)
        
        # 三个按钮宽度统一
        btn_width = 14
        
        self.btn_preview = tk.Button(
            self, command=self.on_preview,
            font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"), relief="flat", 
            bd=0, padx=SPACING_LARGE, pady=6, cursor="hand2", fg="white",
            width=btn_width
        )
        self.btn_preview.grid(row=0, column=1, padx=SPACING_SMALL)
        
        self.btn_rename = tk.Button(
            self, command=self.on_rename,
            font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"), relief="flat",
            bd=0, padx=SPACING_LARGE, pady=6, cursor="hand2", fg="white",
            width=btn_width
        )
        self.btn_rename.grid(row=0, column=2, padx=SPACING_SMALL)
        
        self.undo_btn = tk.Button(
            self, command=self.on_undo,
            font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"), relief="flat",
            bd=0, padx=SPACING_LARGE, pady=6, cursor="hand2", fg="white",
            width=btn_width
        )
        self.undo_btn.grid(row=0, column=3, padx=SPACING_SMALL)
    
    def set_language(self, lang_dict: dict):
        self.btn_preview.config(text=lang_dict['btn_preview'])
        self.btn_rename.config(text=lang_dict['btn_rename'])
        self.undo_btn.config(text=lang_dict['btn_undo'])
    
    def set_undo_state(self, has_history: bool, theme: str):
        colors = THEME_COLORS[theme]
        if has_history:
            self.undo_btn.config(state='normal', bg=colors['accent'], 
                                activebackground=colors['accent_hover'])
        else:
            self.undo_btn.config(state='disabled', bg=colors['tree_heading'])
    
    def apply_theme(self, colors: dict):
        self.configure(bg=colors['bg_main'])
        
        self.btn_preview.config(
            bg=colors['primary'], 
            activebackground=colors['primary_hover'],
            activeforeground='white',
            fg='white'
        )
        
        self.btn_rename.config(
            bg=colors['success'],
            activebackground=colors['success_hover'],
            activeforeground='white',
            fg='white'
        )
        
        if self.undo_btn['state'] != 'disabled':
            self.undo_btn.config(
                bg=colors['accent'],
                activebackground=colors['accent_hover'],
                activeforeground='white',
                fg='white'
            )
        else:
            self.undo_btn.config(
                bg=colors['tree_heading'],
                fg=colors['fg_sub']
            )


class PreviewTable(tk.Frame):
    """预览表格"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self.lbl_preview = tk.Label(
            self, font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold")
        )
        self.lbl_preview.grid(row=0, column=0, sticky='w', pady=(0, ROW_PADDING))
        
        table_frame = tk.Frame(self)
        table_frame.grid(row=1, column=0, sticky='nsew')
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        cols = ('old_name', 'new_name')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings')
        self.scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        
        style = ttk.Style()
        style.configure("Treeview", font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        style.configure("Treeview.Heading", font=(FONT_FAMILY, FONT_SIZE_BOLD, "bold"))
        
        self.tree.heading('old_name', text='原始文件名')
        self.tree.heading('new_name', text='新文件名')
        self.tree.column('old_name', minwidth=200, width=350, anchor='w')
        self.tree.column('new_name', minwidth=200, width=350, anchor='w')
    
    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_items(self, items: list):
        for old_name, new_name in items:
            self.tree.insert('', 'end', values=(old_name, new_name))
    
    def set_language(self, lang_dict: dict):
        self.lbl_preview.config(text=lang_dict['lbl_preview'])
        self.tree.heading('old_name', text=lang_dict['tree_old'])
        self.tree.heading('new_name', text=lang_dict['tree_new'])
    
    def apply_theme(self, colors: dict):
        self.configure(bg=colors['bg_main'])
        self.lbl_preview.config(bg=colors['bg_main'], fg=colors['fg_main'])
        
        style = ttk.Style()
        style.configure("Treeview", 
                       background=colors['bg_card'],
                       fieldbackground=colors['bg_card'],
                       foreground=colors['fg_main'])