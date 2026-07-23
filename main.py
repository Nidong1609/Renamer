import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
import sys
import re
import appdirs

from language import LANG_DICT
from engine import RenameEngine
from view import (
    TopBar, DirSelector, NumRenameTab, OrderRenameTab,
    TimeRenameTab, ReplaceRenameTab, ActionButtons, PreviewTable
)
from theme import ThemeManager, THEME_COLORS


class RenameApp:
    def __init__(self, root):
        self.root = root
        self.engine = RenameEngine()
        
        self.current_lang = 'zh' if 'zh' in LANG_DICT else next(iter(LANG_DICT))
        self.current_theme = 'light'
        self._cancel_requested = False
        
        # 配置文件路径（优先便携模式，否则使用 AppData）
        self.app_name = "BatchRenamer"
        self.app_author = "BatchRenamer"
        self.config_file = self._get_config_path()
        
        root.geometry("920x860")
        root.minsize(880, 820)
        root.geometry(f"+{(root.winfo_screenwidth()-920)//2}+{(root.winfo_screenheight()-860)//2}")
        
        self.theme_manager = ThemeManager(root, ttk.Style())
        
        self._create_ui()
        self.load_config()
        self.apply_theme(self.current_theme)
        self.refresh_language()
        self._clean_leftover_temp_files(self.dir_selector.get_path())
    
    def _get_config_path(self):
        """获取配置文件路径：优先便携模式（exe同目录），否则使用AppData"""
        # 便携模式检测：如果 exe 所在目录存在 config.json，使用它
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            portable_config = os.path.join(exe_dir, "config.json")
            if os.path.exists(portable_config):
                return portable_config
        
        # 否则使用 AppData
        config_dir = appdirs.user_data_dir(self.app_name, self.app_author)
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.json")
    
    def _create_ui(self):
        self.root.columnconfigure(0, weight=1)
        # 行权重：标签页占1份，预览表占6份
        self.root.rowconfigure(2, weight=1)   # 标签页
        self.root.rowconfigure(5, weight=6)   # 预览表（获得绝大部分空间）
        
        self.top_bar = TopBar(
            self.root,
            on_lang_change=self.on_lang_change,
            on_theme_change=self.on_theme_change
        )
        self.top_bar.grid(row=0, column=0, sticky='ew', padx=20, pady=(15, 5))
        
        self.dir_selector = DirSelector(
            self.root,
            on_select=self.on_dir_selected
        )
        self.dir_selector.grid(row=1, column=0, sticky='ew', padx=20, pady=5)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=2, column=0, sticky='nsew', padx=20, pady=5)
        
        # 4个标签页
        self.num_tab = NumRenameTab(self.notebook)
        self.order_tab = OrderRenameTab(self.notebook)
        self.time_tab = TimeRenameTab(self.notebook)
        self.replace_tab = ReplaceRenameTab(self.notebook)
        
        self.notebook.add(self.num_tab, text="序号重命名")
        self.notebook.add(self.order_tab, text="按顺序重命名")
        self.notebook.add(self.time_tab, text="按时间重命名")
        self.notebook.add(self.replace_tab, text="查找与替换")
        
        self.buttons = ActionButtons(
            self.root,
            on_preview=self.start_preview,
            on_rename=self.start_rename,
            on_undo=self.start_undo
        )
        self.buttons.grid(row=3, column=0, pady=(3, 0))
        
        self.progress_bar = ttk.Progressbar(
            self.root, orient="horizontal", mode="determinate"
        )
        self.progress_bar.grid(row=4, column=0, sticky="ew", padx=20, pady=(2, 3))
        
        self.preview_table = PreviewTable(self.root)
        self.preview_table.grid(row=5, column=0, sticky='nsew', padx=20, pady=(3, 15))
    
    def on_dir_selected(self, path):
        self.preview_table.clear()
        self._clean_leftover_temp_files(path)
        self.save_config()

    def _clean_leftover_temp_files(self, directory):
        """
        检查并清理上次程序异常退出后遗留的临时文件（engine 里早就写好了这个方法，
        但之前从未被调用过，导致崩溃残留的 __temp_rename__ 文件永远不会被自动恢复）。
        """
        if not directory:
            return
        try:
            recovered = self.engine.check_and_clean_temp_files(directory)
        except Exception:
            return
        if recovered:
            lang = LANG_DICT[self.current_lang]
            # 该提示原来是按 zh/其他 二分的，现在统一走翻译表，
            # 缺失时兜底为英文，保证以后新增语言不会崩
            fallback = "Found {} leftover temp file(s) from a previous crash; restored their original names."
            msg = lang.get('msg_temp_recovered', fallback).format(len(recovered))
            messagebox.showinfo(lang['msg_title_notice'], msg)
    
    def on_lang_change(self, new_lang):
        """new_lang 由 TopBar 根据下拉框位置直接换算出的语言代码传入，
        不再需要在这里解析下拉框里显示的具体文字"""
        if self.current_lang != new_lang:
            self.current_lang = new_lang
            self.refresh_language()
            self.save_config()
    
    def on_theme_change(self, new_theme):
        """new_theme 由 TopBar 根据下拉框位置直接换算出的主题代码('light'/'dark')传入"""
        self.apply_theme(new_theme)
        self.save_config()
    
    def apply_theme(self, theme):
        colors = self.theme_manager.apply_theme(theme)
        self.current_theme = theme
    
        self.top_bar.apply_theme(colors)
        self.dir_selector.apply_theme(colors)
        self.num_tab.apply_theme(colors)
        self.order_tab.apply_theme(colors)
        self.time_tab.apply_theme(colors)
        self.replace_tab.apply_theme(colors)
        self.buttons.apply_theme(colors)
        self.preview_table.apply_theme(colors)
    
        style = ttk.Style()
        style.configure("TProgressbar", 
                       background=colors['primary'],
                       troughcolor=colors['tree_heading'],
                       bordercolor=colors['border'],
                       lightcolor=colors['border'],
                       darkcolor=colors['border'])
        self.progress_bar.configure(style="TProgressbar")
    
        has_history = bool(self.engine.undo_history and self.engine.undo_dir)
        self.buttons.set_undo_state(has_history, theme)
        
        self.buttons.btn_preview.config(bg=colors['primary'])
        self.buttons.btn_rename.config(bg=colors['success'])
        
        tree = self.preview_table.tree
        for item in tree.get_children():
            tree.item(item, tags=())
        
        for i, item in enumerate(tree.get_children()):
            if i % 2 == 0:
                tree.item(item, tags=('evenrow',))
            else:
                tree.item(item, tags=('oddrow',))
        
        if theme == 'dark':
            tree.tag_configure('evenrow', background=colors['bg_card'])
            tree.tag_configure('oddrow', background='#1E2233')
        else:
            tree.tag_configure('evenrow', background='#FFFFFF')
            tree.tag_configure('oddrow', background='#F8F9FA')
    
    def refresh_language(self):
        lang = LANG_DICT[self.current_lang]
    
        self.top_bar.set_language(self.current_lang, lang)
        self.dir_selector.set_language(lang)
        self.num_tab.set_language(lang)
        self.order_tab.set_language(lang)
        self.time_tab.set_language(lang)
        self.replace_tab.set_language(lang)
        self.buttons.set_language(lang)
        self.preview_table.set_language(lang)
    
        self.notebook.tab(0, text=lang['tab_num'])
        self.notebook.tab(1, text=lang['tab_order'])
        self.notebook.tab(2, text=lang['tab_time'])
        self.notebook.tab(3, text=lang['tab_replace'])
    
        self.root.title(lang['title'])
    
        placeholder = lang['prefix_placeholder']
        self.num_tab.set_prefix_placeholder(placeholder, self.theme_manager.current_theme)
        self.order_tab.set_prefix_placeholder(placeholder, self.theme_manager.current_theme)
        self.time_tab.set_prefix_placeholder(placeholder, self.theme_manager.current_theme)
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    loaded_lang = config.get("language", "zh")
                    # 配置文件里存的语言代码如果不在当前 language.py 里了（比如
                    # 语言文件被精简过），就退回默认语言，避免 KeyError
                    self.current_lang = loaded_lang if loaded_lang in LANG_DICT else self.current_lang
                    theme = config.get("theme", "light")
                    self.dir_selector.set_path(config.get("target_dir", ""))
                    
                    # 这里只记录主题代码，具体下拉框的文字和选中项交给
                    # 随后 __init__ 里调用的 refresh_language() 统一渲染
                    self.top_bar.set_theme_code(theme)
                    self.apply_theme(theme)
            except:
                pass
    
    def save_config(self):
        try:
            # 如果是便携模式，确保目录存在（通常已存在）
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "language": self.current_lang,
                    "theme": self.theme_manager.current_theme,
                    "target_dir": self.dir_selector.get_path()
                }, f, ensure_ascii=False, indent=4)
        except:
            pass
    
    def _iter_all_descendants(self, widget):
        """递归遍历widget的所有后代控件（不仅仅是直接子控件）"""
        for child in widget.winfo_children():
            yield child
            yield from self._iter_all_descendants(child)

    def set_ui_state(self, state):
        is_normal = (state == "normal")
        
        self.buttons.btn_preview.config(state=state)
        self.buttons.btn_rename.config(state=state)
        self.buttons.undo_btn.config(state=state)
        self.dir_selector.btn_browse.config(state=state)
        
        self.dir_selector.entry_dir.config(state=state)
        self.top_bar.lang_combo.config(state="readonly" if is_normal else "disabled")
        self.top_bar.theme_combo.config(state="readonly" if is_normal else "disabled")
        
        # 锁定所有标签页的输入（递归遍历，因为实际输入框都嵌套在 LabelFrame/Frame 内部）
        for tab in [self.num_tab, self.order_tab, self.time_tab, self.replace_tab]:
            for child in self._iter_all_descendants(tab):
                if isinstance(child, (tk.Entry, tk.Spinbox)):
                    try:
                        child.config(state=state)
                    except:
                        pass
                elif isinstance(child, ttk.Combobox):
                    try:
                        child.config(state="readonly" if is_normal else "disabled")
                    except:
                        pass
        
        if is_normal:
            self.notebook.state(["!disabled"])
            self.num_tab._toggle_prefix()
            self.order_tab._toggle_prefix()
            self.time_tab._toggle_prefix()
        else:
            self.notebook.state(["disabled"])
    
    def update_progress(self, current, total):
        self.root.after(0, lambda: self._update_progress_ui(current, total))
    
    def _update_progress_ui(self, current, total):
        self.progress_bar['max'] = total
        self.progress_bar['value'] = current
    
    def _parse_new_start(self, raw_value, lang):
        """解析起始编号；失败时弹窗提示并返回 None，成功时返回 int"""
        try:
            return int(raw_value or 1)
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror(
                lang['msg_title_err'], lang['msg_invalid_num']
            ))
            return None
    
    def _resolve_prefix(self, prefix, lang):
        """输入框仍显示占位符文本时，视为用户未填写，返回空字符串"""
        return "" if prefix == lang['prefix_placeholder'] else prefix
    
    def _validate_pad_width(self, pad_width, lang):
        """校验补零位数是否在合法范围内；非法时弹窗提示并返回 False"""
        if pad_width < 0 or pad_width > 10:
            self.root.after(0, lambda: messagebox.showerror(
                lang['msg_title_err'], lang['msg_invalid_pad']
            ))
            return False
        return True
    
    def start_preview(self):
        self.set_ui_state("disabled")
        threading.Thread(target=self.do_preview, daemon=True).start()
    
    def do_preview(self):
        lang = LANG_DICT[self.current_lang]
        self.preview_table.clear()
        self.engine.clear_preview_data()
        
        try:
            current_tab = self.notebook.index(self.notebook.select())
            directory = self.dir_selector.get_path()
            
            if not directory:
                self.root.after(0, lambda: messagebox.showwarning(
                    lang['msg_title_warn'], lang['msg_select_dir']
                ))
                return
            
            if current_tab == 0:
                # 序号重命名 - 使用高级预览方法
                values = self.num_tab.get_values()
                
                # 验证输入
                new_start = self._parse_new_start(values['new_start'], lang)
                if new_start is None:
                    return
                
                pad_width = values.get('pad_width', 0)
                if not self._validate_pad_width(pad_width, lang):
                    return
                
                # 解析"当前编号范围"：两个都留空则不做范围过滤（处理全部文件）
                old_start_str = str(values.get('old_start', '')).strip()
                old_end_str = str(values.get('old_end', '')).strip()
                
                if old_start_str or old_end_str:
                    try:
                        old_start = int(old_start_str)
                        old_end = int(old_end_str)
                    except ValueError:
                        self.root.after(0, lambda: messagebox.showerror(
                            lang['msg_title_err'], lang['msg_invalid_num']
                        ))
                        return
                    
                    if old_end < old_start:
                        self.root.after(0, lambda: messagebox.showerror(
                            lang['msg_title_err'], lang['msg_range_err']
                        ))
                        return
                else:
                    old_start = None
                    old_end = None
                
                # 获取文件
                files = self.engine.get_files_by_range(directory, values['extensions'])
                if not files:
                    self.root.after(0, lambda: messagebox.showwarning(
                        lang['msg_title_warn'], lang['msg_no_files']
                    ))
                    return
                
                prefix = self._resolve_prefix(values['prefix'], lang)
                
                # 使用高级预览方法（按当前编号范围过滤，仅对范围内的文件重新编号）
                preview_data = self.engine.generate_preview_num_advanced(
                    files=files,
                    new_start=new_start,
                    prefix=prefix,
                    only_num=values['only_num'],
                    num_group=values.get('num_group', 1),
                    reverse=values.get('reverse', False),
                    pad_width=pad_width,
                    is_prefix=values.get('is_prefix', True),
                    old_start=old_start,
                    old_end=old_end
                )
                
            elif current_tab == 1:
                # 按顺序重命名
                values = self.order_tab.get_values()
                
                new_start = self._parse_new_start(values['new_start'], lang)
                if new_start is None:
                    return
                
                if not self._validate_pad_width(values['pad_width'], lang):
                    return
                
                files = self.engine.get_files_by_order(directory, values['extensions'])
                if not files:
                    self.root.after(0, lambda: messagebox.showwarning(
                        lang['msg_title_warn'], lang['msg_no_files']
                    ))
                    return
                
                prefix = self._resolve_prefix(values['prefix'], lang)
                
                preview_data = self.engine.generate_preview_order(
                    files=files,
                    prefix=prefix,
                    only_num=values['only_num'],
                    pad_width=values['pad_width'],
                    reverse=values['reverse'],
                    new_start=new_start,
                    is_prefix=values.get('is_prefix', True),
                    sort_by_name=True
                )
                
            elif current_tab == 2:
                # 按时间重命名
                values = self.time_tab.get_values()
                
                new_start = self._parse_new_start(values['new_start'], lang)
                if new_start is None:
                    return
                
                if not self._validate_pad_width(values['pad_width'], lang):
                    return
                
                files = self.engine.get_files_by_time(directory, values['extensions'], reverse=False)
                if not files:
                    self.root.after(0, lambda: messagebox.showwarning(
                        lang['msg_title_warn'], lang['msg_no_files']
                    ))
                    return
                
                prefix = self._resolve_prefix(values['prefix'], lang)
                
                preview_data = self.engine.generate_preview_order(
                    files=files,
                    prefix=prefix,
                    only_num=values['only_num'],
                    pad_width=values['pad_width'],
                    reverse=values['reverse'],
                    new_start=new_start,
                    is_prefix=values.get('is_prefix', True),
                    sort_by_name=False
                )
                
            else:
                # 查找替换 (tab 3)
                values = self.replace_tab.get_values()
                files = self.engine.get_files_by_range(directory, values['extensions'])
                if not files:
                    self.root.after(0, lambda: messagebox.showwarning(
                        lang['msg_title_warn'], lang['msg_no_files']
                    ))
                    return
                
                # 如果查找文本为空，提示
                if not values['find'].strip():
                    self.root.after(0, lambda: messagebox.showwarning(
                        lang['msg_title_warn'], lang.get('msg_find_empty', "Please enter the text to find")
                    ))
                    return
                
                preview_data = self.engine.generate_preview_replace(
                    files, values['find'], values['replace'], values['use_regex']
                )
            
            if not preview_data:
                self.root.after(0, lambda: messagebox.showwarning(
                    lang['msg_title_warn'], lang['msg_no_files']
                ))
                return
            
            preview_items = [(item['old_name'], item['new_name']) for item in preview_data]
            self.root.after(0, lambda: self.preview_table.add_items(preview_items))
        
        except re.error:
            self.root.after(0, lambda: messagebox.showerror(
                lang['msg_title_err'], lang['msg_regex_err']
            ))
        except ValueError as e:
            self.root.after(0, lambda: messagebox.showerror(
                lang['msg_title_err'], str(e) if str(e) else lang['msg_invalid_num']
            ))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                lang['msg_title_err'], lang['msg_read_dir_failed'].format(str(e))
            ))
        finally:
            self.root.after(0, lambda: self.set_ui_state("normal"))
    
    def start_rename(self):
        lang = LANG_DICT[self.current_lang]
        
        if not self.engine.preview_data:
            messagebox.showwarning(lang['msg_title_notice'], lang['msg_preview_first'])
            return
        
        if not messagebox.askyesno(
            lang['msg_title_confirm'],
            lang['msg_confirm_rename'].format(len(self.engine.preview_data))
        ):
            return
        
        self.set_ui_state("disabled")
        threading.Thread(target=self.do_rename, daemon=True).start()
    
    def do_rename(self):
        lang = LANG_DICT[self.current_lang]
        try:
            self.engine.execute_rename(
                progress_callback=self.update_progress
            )
            self.root.after(0, lambda: messagebox.showinfo(
                lang['msg_title_success'], lang['msg_rename_success']
            ))
            self.root.after(0, self.preview_table.clear)
        except PermissionError:
            self.root.after(0, lambda: messagebox.showerror(
                lang['msg_title_err'], lang['msg_file_busy']
            ))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                lang['msg_title_err'], lang['msg_rename_failed'].format(str(e))
            ))
        finally:
            self.root.after(0, lambda: self._reset_ui_after_operation())
    
    def start_undo(self):
        lang = LANG_DICT[self.current_lang]
        
        if not self.engine.undo_history or not self.engine.undo_dir:
            messagebox.showwarning(lang['msg_title_notice'], lang['msg_no_undo_history'])
            return
        
        if not messagebox.askyesno(
            lang['msg_title_confirm'],
            lang['msg_confirm_undo'].format(len(self.engine.undo_history[-1]))
        ):
            return
        
        self.set_ui_state("disabled")
        threading.Thread(target=self.do_undo, daemon=True).start()
    
    def do_undo(self):
        lang = LANG_DICT[self.current_lang]
        try:
            self.engine.undo_rename(progress_callback=self.update_progress)
            self.root.after(0, lambda: messagebox.showinfo(
                lang['msg_title_success'], lang['msg_undo_success']
            ))
            self.root.after(0, self.preview_table.clear)
        except PermissionError:
            self.root.after(0, lambda: messagebox.showerror(
                lang['msg_title_err'], lang['msg_file_busy']
            ))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                lang['msg_title_err'], lang['msg_undo_failed'].format(str(e))
            ))
        finally:
            self.root.after(0, lambda: self._reset_ui_after_operation())
    
    def _reset_ui_after_operation(self):
        self.update_progress(0, 1)
        self.set_ui_state("normal")
        self.refresh_language()
        self.apply_theme(self.theme_manager.current_theme)


if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    root = tk.Tk()
    app = RenameApp(root)
    root.mainloop()